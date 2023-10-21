document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, заблокированы ли рекламные элементы
    var adBlocked = false;
    var adContainer = document.getElementById('ad-container');

    if (adContainer) {
    var testAd = document.createElement('div');
    testAd.innerHTML = '&nbsp;';
    testAd.style.width = '1px';
    testAd.style.height = '1px';
    testAd.style.position = 'absolute';
    testAd.style.top = '-10px'; // Переместите тестовый элемент выше видимой области страницы
    adContainer.appendChild(testAd);

    window.setTimeout(function() {
        if (testAd.offsetHeight === 0) {
            adBlocked = true;
        }
        testAd.remove(); // Удаляем тестовый элемент
        // Ваш код для обработки результата
        if (adBlocked) {
            console.log('(AdBlock) обнаружен.');
            // Здесь вы можете выполнить действия, связанные с обнаружением AdBlock
        } else {
            console.log(' (AdBlock) не обнаружен.');
            // Здесь вы можете выполнить действия, если AdBlock не обнаружен
        }
        }, 100);
    }
});