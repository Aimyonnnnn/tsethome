document.addEventListener("DOMContentLoaded", function () {
    // Swiper 초기화
    var educationSwiper = new Swiper('.education-swiper-container', {
        slidesPerView: 1,
        spaceBetween: 10,
        pagination: {
            el: '.education-swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.education-swiper-button-next',
            prevEl: '.education-swiper-button-prev',
        },
        loop: true, // 필요에 따라 설정 변경
    });
});
