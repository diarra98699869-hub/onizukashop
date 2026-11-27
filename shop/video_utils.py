"""
ONIZUKA SHOP - Gestion, Validation, Découpe (15s max) et Compression Automatique (8 Mo max) des Vidéos Produits
Compatible FFmpeg serveur + Analyseur natif MP4/MOV Python sans dépendance externe.
"""
import os
import re
import shutil
import struct
import subprocess
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

MAX_VIDEO_DURATION_SECONDS = 15.0
MAX_VIDEO_SIZE_MB = 8.0
MAX_VIDEO_SIZE_BYTES = int(MAX_VIDEO_SIZE_MB * 1024 * 1024)  # 8 388 608 octets
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm', '.m4v'}


def find_ffmpeg_binary():
    """Localise l'exécutable ffmpeg sur le serveur (PATH ou installation WinGet/Linux)."""
    path = shutil.which('ffmpeg')
    if path:
        return path
    candidates = [
        r'C:\Users\a\AppData\Local\Microsoft\WinGet\Links\ffmpeg.EXE',
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def parse_mp4_duration_native(file_path):
    """
    Lit la durée exacte (en secondes) d'un fichier MP4/MOV/M4V directement depuis l'atome ISO BMFF 'mvhd'
    en pur Python (0 dépendance externe, exécution < 1ms).
    """
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            def search_boxes(start, end, depth=0):
                if depth > 4:
                    return None
                pos = start
                while pos + 8 <= end:
                    f.seek(pos)
                    header = f.read(8)
                    if len(header) < 8:
                        break
                    box_size, box_type = struct.unpack('>I4s', header)
                    header_size = 8
                    if box_size == 1:
                        large = f.read(8)
                        if len(large) < 8:
                            break
                        box_size = struct.unpack('>Q', large)[0]
                        header_size = 16
                    elif box_size == 0:
                        box_size = end - pos
                    if box_size < header_size or pos + box_size > end:
                        break

                    if box_type == b'moov':
                        res = search_boxes(pos + header_size, pos + box_size, depth + 1)
                        if res is not None:
                            return res
                    elif box_type == b'mvhd':
                        f.seek(pos + header_size)
                        mvhd_data = f.read(32)
                        if len(mvhd_data) >= 20:
                            version = mvhd_data[0]
                            if version == 0:
                                timescale, duration = struct.unpack('>II', mvhd_data[12:20])
                            elif version == 1 and len(mvhd_data) >= 32:
                                timescale, duration = struct.unpack('>IQ', mvhd_data[20:32])
                            else:
                                return None
                            if timescale > 0 and duration > 0:
                                return round(duration / float(timescale), 2)
                    pos += box_size
                return None

            return search_boxes(0, file_size)
    except Exception:
        return None


def get_video_duration_ffmpeg(file_path, ffmpeg_bin=None):
    """Récupère la durée d'une vidéo via ffmpeg -i ou l'analyseur natif MP4."""
    native_dur = parse_mp4_duration_native(file_path)
    if native_dur is not None and native_dur > 0:
        return native_dur

    ffmpeg_bin = ffmpeg_bin or find_ffmpeg_binary()
    if not ffmpeg_bin:
        return None

    try:
        proc = subprocess.run(
            [ffmpeg_bin, '-hide_banner', '-i', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        output = proc.stderr or proc.stdout or ''
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', output)
        if m:
            h, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return round(h * 3600 + mins * 60 + secs, 2)
    except Exception:
        pass
    return None


def process_uploaded_product_video(uploaded_file):
    """
    Vérifie et optimise une vidéo produit téléversée :
    - Limite stricte : <= 15 secondes et <= 8 Mo.
    - Si la vidéo dépasse 15s ou 8 Mo (ou est en .mov lourd), FFmpeg la coupe automatiquement à 15s
      et la compresse en MP4 H.264 Web-optimisé (< 8 Mo, 720p fluide, faststart).
    - Retourne (processed_file, info_dict)
    """
    if not uploaded_file:
        return None, {}

    orig_name = getattr(uploaded_file, 'name', 'video.mp4')
    ext = os.path.splitext(orig_name)[1].lower() or '.mp4'
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            f"Format vidéo non supporté ({ext}). Utilisez MP4, MOV ou WebM (max 15s et 8 Mo)."
        )

    orig_size = getattr(uploaded_file, 'size', 0)
    orig_size_mb = round(orig_size / (1024 * 1024), 2)

    # Écrire dans un fichier temporaire pour inspection / compression
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        for chunk in uploaded_file.chunks() if hasattr(uploaded_file, 'chunks') else [uploaded_file.read()]:
            tmp_in.write(chunk)
        tmp_in_path = tmp_in.name

    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(0)

    ffmpeg_bin = find_ffmpeg_binary()
    duration = get_video_duration_ffmpeg(tmp_in_path, ffmpeg_bin=ffmpeg_bin)

    needs_trim = duration is not None and duration > (MAX_VIDEO_DURATION_SECONDS + 0.4)
    needs_compress = orig_size > MAX_VIDEO_SIZE_BYTES
    needs_transcode = ext in ('.mov', '.m4v')

    info = {
        'original_size_mb': orig_size_mb,
        'original_duration': duration,
        'final_size_mb': orig_size_mb,
        'final_duration': min(duration, MAX_VIDEO_DURATION_SECONDS) if duration else None,
        'was_trimmed': False,
        'was_compressed': False,
        'summary': '',
    }

    try:
        # Si la vidéo est déjà <= 15s, <= 8 Mo et en MP4/WebM standard : on la garde telle quelle !
        if not needs_trim and not needs_compress and not needs_transcode:
            return uploaded_file, info

        # Si dépassement mais FFmpeg absent sur le serveur
        if not ffmpeg_bin:
            reasons = []
            if needs_trim:
                reasons.append(f"durée de {duration:.1f}s (max {int(MAX_VIDEO_DURATION_SECONDS)}s)")
            if needs_compress:
                reasons.append(f"taille de {orig_size_mb} Mo (max {int(MAX_VIDEO_SIZE_MB)} Mo)")
            raise ValidationError(
                f"La vidéo dépasse les limites autorisées ({', '.join(reasons)}). "
                f"Veuillez utiliser le bouton de compression intégré ou choisir une vidéo de max 15s et 8 Mo."
            )

        # Compression & Découpe automatique FFmpeg à 15s max et < 8 Mo
        tmp_out_fd, tmp_out_path = tempfile.mkstemp(suffix='.mp4')
        os.close(tmp_out_fd)

        try:
            # Cible débit : pour 15s sous 7.2 Mo max -> ~3200 kbps total (2800k vidéo + 96k audio)
            cmd = [
                ffmpeg_bin, '-y', '-hide_banner', '-loglevel', 'error',
                '-i', tmp_in_path,
                '-t', str(int(MAX_VIDEO_DURATION_SECONDS)),
                '-vf', "scale='min(720,iw)':-2",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '26',
                '-maxrate', '2600k',
                '-bufsize', '5200k',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-c:a', 'aac',
                '-b:a', '96k',
                tmp_out_path,
            ]
            subprocess.run(cmd, check=True, timeout=60)

            out_size = os.path.getsize(tmp_out_path)

            # Passe de sécurité si jamais le fichier dépasse encore 8 Mo
            if out_size > MAX_VIDEO_SIZE_BYTES:
                cmd_tight = [
                    ffmpeg_bin, '-y', '-hide_banner', '-loglevel', 'error',
                    '-i', tmp_in_path,
                    '-t', str(int(MAX_VIDEO_DURATION_SECONDS)),
                    '-vf', "scale='min(540,iw)':-2",
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-crf', '30',
                    '-maxrate', '1800k',
                    '-bufsize', '3600k',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    '-c:a', 'aac',
                    '-b:a', '64k',
                    tmp_out_path,
                ]
                subprocess.run(cmd_tight, check=True, timeout=60)
                out_size = os.path.getsize(tmp_out_path)

            if out_size > MAX_VIDEO_SIZE_BYTES:
                raise ValidationError(
                    f"Même après compression, la vidéo fait {out_size / (1024*1024):.1f} Mo (limite : 8 Mo)."
                )

            with open(tmp_out_path, 'rb') as f_out:
                video_bytes = f_out.read()

            final_dur = get_video_duration_ffmpeg(tmp_out_path, ffmpeg_bin=ffmpeg_bin) or min(
                duration or MAX_VIDEO_DURATION_SECONDS, MAX_VIDEO_DURATION_SECONDS
            )
            final_mb = round(len(video_bytes) / (1024 * 1024), 2)

            base_stem = os.path.splitext(os.path.basename(orig_name))[0]
            clean_stem = re.sub(r'[^a-zA-Z0-9_-]+', '_', base_stem)[:45] or 'video_produit'
            new_filename = f"{clean_stem}_15s.mp4"

            processed_file = SimpleUploadedFile(
                name=new_filename,
                content=video_bytes,
                content_type='video/mp4',
            )

            info['final_size_mb'] = final_mb
            info['final_duration'] = final_dur
            info['was_trimmed'] = bool(needs_trim)
            info['was_compressed'] = bool(needs_compress or len(video_bytes) < orig_size or needs_transcode)

            actions = []
            if info['was_trimmed']:
                actions.append(f"coupée à {final_dur:.0f}s (au lieu de {duration:.0f}s)")
            if info['was_compressed']:
                actions.append(f"compressée de {orig_size_mb} Mo à {final_mb} Mo")
            if actions:
                info['summary'] = f"Vidéo optimisée automatiquement ({', '.join(actions)})."

            return processed_file, info
        finally:
            if os.path.exists(tmp_out_path):
                try:
                    os.remove(tmp_out_path)
                except OSError:
                    pass
    finally:
        if os.path.exists(tmp_in_path):
            try:
                os.remove(tmp_in_path)
            except OSError:
                pass
