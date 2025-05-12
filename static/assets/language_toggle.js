document.addEventListener('DOMContentLoaded', () => {
  const languageToggle = document.getElementById('language-toggle');
  const languageTooltipText = document.getElementById('language-tooltip');

  // Determine current language based on the URL pathname.
  // Persian (default) has no prefix, while English uses a "/en" prefix.
  const currentUrl = new URL(window.location.href);
  let isEnglish = currentUrl.pathname.startsWith('/en');

  // Determine the target language based on current URL.
  // If we're in Persian (isEnglish is false), then the target is English ('en').
  // If we're in English, then the target is Persian ('fa').
  const targetLang = isEnglish ? 'fa' : 'en';

  // Set the tooltip text based on the current state.
  languageTooltipText.textContent = isEnglish ? 'تغییر به فارسی' : 'Change to English';

  languageToggle.addEventListener('click', () => {
    // Recompute current URL and language state on click.
    const currentUrl = new URL(window.location.href);
    const pathname = currentUrl.pathname;
    const isEnglish = pathname.startsWith('/en');
    const targetLang = isEnglish ? 'fa' : 'en';
    let newUrl = '';

    if (!isEnglish) {
      // We are in the Persian view, so add the "/en" prefix.
      newUrl = currentUrl.origin + '/en' + pathname + currentUrl.search;
    } else {
      // We are in the English view, so remove the "/en" prefix.
      newUrl = currentUrl.origin + pathname.replace(/^\/en/, '') + currentUrl.search;
    }

    // Call the language-switching endpoint.
    fetch(`/common/switch-language/${targetLang}/`, {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin'
    })
    .then(() => {
      // After the language cookie/session is updated, redirect to the new URL.
      window.location.href = newUrl;
    })
    .catch((err) => console.error('Error switching language:', err));
  });
});
