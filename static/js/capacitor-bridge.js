/**
 * ONIZUKA SHOP - Pont Unifié PWA Pro & Capacitor Mobile Native (Android / iOS)
 * Gère : Installation PWA 1-Tap, Barre de statut native, SplashScreen, Bouton Retour Android,
 * Retour Haptique (Vibrations), Partage Natif et Détection Réseau Hors-Ligne à Bamako.
 */
(function () {
  'use strict';

  const OnizukaNative = {
    deferredPrompt: null,
    canInstall: false,
    installPlatform: null,
    isCapacitor: Boolean(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()),
    isStandalone: Boolean(
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true ||
      (window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform())
    ),
    isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream,

    init() {
      this.setupPWAInstall();
      this.setupCapacitorPlugins();
      this.setupExternalIntentLinks();
      this.setupNetworkMonitor();
      this.exposeHelpers();
    },

    /* 1bis. INTERCEPTION NATIVE DES LIENS WHATSAPP, TÉLÉPHONE & EMAIL DANS L'APK ANDROID/iOS */
    setupExternalIntentLinks() {
      document.addEventListener('click', (e) => {
        const a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
        if (!a) return;
        const href = (a.getAttribute('href') || '').trim();
        if (!href) return;

        const isWhatsApp = href.includes('wa.me/') || href.includes('api.whatsapp.com') || href.startsWith('whatsapp://');
        const isNativeScheme = href.startsWith('tel:') || href.startsWith('mailto:') || href.startsWith('sms:');

        if (isWhatsApp || isNativeScheme) {
          this.haptic('light');
          if (this.isCapacitor && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Browser && isWhatsApp) {
            e.preventDefault();
            window.Capacitor.Plugins.Browser.open({ url: href }).catch(() => {
              window.open(href, '_system');
            });
          }
        }
      }, { passive: false });
    },

    /* 1. INSTALLATION PWA 1-CLIC (ANDROID / CHROME / EDGE / DESKTOP & GUIDE iOS) */
    setupPWAInstall() {
      if (this.isStandalone) return;

      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        this.deferredPrompt = e;
        this.canInstall = true;
        this.installPlatform = 'prompt';
        document.documentElement.classList.add('pwa-installable');
        window.dispatchEvent(new CustomEvent('pwa-install-available', { detail: { platform: 'prompt' } }));
      });

      window.addEventListener('appinstalled', () => {
        this.deferredPrompt = null;
        this.canInstall = false;
        this.isStandalone = true;
        document.documentElement.classList.remove('pwa-installable');
        window.dispatchEvent(new CustomEvent('pwa-installed'));
      });

      // Sur iOS Safari non installé, signaler que le guide d'ajout à l'écran d'accueil est disponible
      if (this.isIOS && !this.isStandalone) {
        this.canInstall = true;
        this.installPlatform = 'ios';
        document.documentElement.classList.add('pwa-ios-installable');
        window.dispatchEvent(new CustomEvent('pwa-install-available', { detail: { platform: 'ios' } }));
      }
    },

    async triggerInstall() {
      if (this.deferredPrompt) {
        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        if (outcome === 'accepted') {
          this.deferredPrompt = null;
        }
        return outcome;
      }
      if (this.isIOS && !this.isStandalone) {
        window.dispatchEvent(new CustomEvent('pwa-show-ios-guide'));
        return 'ios-guide';
      }
      return 'unavailable';
    },

    /* 2. PLUGINS CAPACITOR NATIFS (ANDROID / iOS) */
    async setupCapacitorPlugins() {
      if (!window.Capacitor || !window.Capacitor.Plugins) return;
      const Plugins = window.Capacitor.Plugins;

      // A. Barre de statut Obsidian (#0d0e12)
      try {
        if (Plugins.StatusBar) {
          await Plugins.StatusBar.setBackgroundColor({ color: '#0d0e12' });
          await Plugins.StatusBar.setStyle({ style: 'DARK' });
        }
      } catch (e) {}

      // B. Masquage fluide du SplashScreen natif
      try {
        if (Plugins.SplashScreen) {
          setTimeout(() => {
            Plugins.SplashScreen.hide({ fadeOutDuration: 250 }).catch(() => {});
          }, 150);
        }
      } catch (e) {}

      // C. Bouton Retour Matériel Android (ferme d'abord les tiroirs/modales, sinon historique)
      try {
        if (Plugins.App) {
          Plugins.App.addListener('backButton', ({ canGoBack }) => {
            const escEvt = new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, bubbles: true });
            window.dispatchEvent(escEvt);
            document.dispatchEvent(escEvt);

            if (canGoBack && window.history.length > 1 && window.location.pathname !== '/') {
              window.history.back();
            } else if (window.location.pathname !== '/') {
              window.location.href = '/';
            } else {
              Plugins.App.exitApp();
            }
          });
        }
      } catch (e) {}
    },

    /* 3. RETOUR HAPTIQUE & PARTAGE NATIF */
    haptic(type) {
      try {
        if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Haptics) {
          if (type === 'success') {
            window.Capacitor.Plugins.Haptics.notification({ type: 'SUCCESS' });
          } else {
            window.Capacitor.Plugins.Haptics.impact({ style: 'LIGHT' });
          }
          return;
        }
        if (navigator.vibrate) {
          navigator.vibrate(type === 'success' ? [12, 30, 18] : 6);
        }
      } catch (e) {}
    },

    async share(opts) {
      const data = {
        title: (opts && opts.title) || document.title || 'Onizuka Shop Bamako',
        text: (opts && opts.text) || 'Découvrez cet article chez Onizuka Shop au Grand Marché de Bamako (+223 92 67 37 99)',
        url: (opts && opts.url) || window.location.href
      };
      try {
        if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Share) {
          await window.Capacitor.Plugins.Share.share(data);
          return true;
        }
        if (navigator.share) {
          await navigator.share(data);
          return true;
        }
      } catch (e) {}
      try {
        await navigator.clipboard.writeText(data.url);
        return 'copied';
      } catch (e) {
        return false;
      }
    },

    /* 4. SURVEILLANCE RÉSEAU 3G/4G BAMAKO */
    setupNetworkMonitor() {
      const showNetToast = (online) => {
        let banner = document.getElementById('onz-network-banner');
        if (online) {
          if (banner) {
            banner.textContent = '✓ Connexion rétablie';
            banner.style.backgroundColor = '#059669';
            setTimeout(() => banner.remove(), 1800);
          }
          return;
        }
        if (!banner) {
          banner = document.createElement('div');
          banner.id = 'onz-network-banner';
          banner.style.cssText = 'position:fixed;bottom:68px;left:12px;right:12px;z-index:9998;padding:10px 14px;border-radius:12px;background:#0d0e12;color:#fde047;border:1px solid rgba(250,204,21,0.35);font-size:12px;font-weight:700;text-align:center;box-shadow:0 10px 25px rgba(0,0,0,0.35);';
          document.body.appendChild(banner);
        }
        banner.textContent = '⚡ Mode hors-ligne actif • WhatsApp Direct : +223 92 67 37 99';
      };

      window.addEventListener('offline', () => showNetToast(false));
      window.addEventListener('online', () => showNetToast(true));
    },

    exposeHelpers() {
      window.OnizukaNative = this;
      window.onizukaHaptic = (t) => this.haptic(t);
      window.onizukaShare = (o) => this.share(o);
      window.onizukaInstallPWA = () => this.triggerInstall();

      document.addEventListener('cartUpdated', () => this.haptic('success'));
      document.addEventListener('wishlistUpdated', () => this.haptic('light'));
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => OnizukaNative.init());
  } else {
    OnizukaNative.init();
  }
})();
