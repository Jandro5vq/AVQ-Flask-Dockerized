var userLang = navigator.language || navigator.userLanguage;
console.log("The language is: " + userLang.slice(0, -3));

// Function to fetch language data
async function fetchLanguageData(lang) {
    const response = await fetch(`/static/lan/portfolio/${lang}.json`);
    return response.json();
}

// Function to update content based on selected language
function updateContent(langData) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = langData[key];
    });
}

// Function to change language
async function changeLanguage(lang) {
    const langData = await fetchLanguageData(lang);
    updateContent(langData);
}

// Call updateContent() on page load
window.addEventListener('DOMContentLoaded', async () => {
    const userPreferredLanguage = userLang.slice(0, -3) || 'es';
    const langData = await fetchLanguageData(userPreferredLanguage);
    updateContent(langData);
});
