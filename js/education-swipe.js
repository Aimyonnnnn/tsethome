
document.addEventListener("DOMContentLoaded", function () {
    // 슬라이드 관련 요소들
    const slides = document.querySelectorAll(".education-swiper-slide");
    const menuItems = document.querySelectorAll(".education-menu-item");
    const prevButton = document.querySelector(".education-swiper-button-prev");
    const nextButton = document.querySelector(".education-swiper-button-next");
    let currentIndex = 0;

    // 슬라이드 변경 함수
    function changeSlide(index) {
        // 모든 슬라이드와 메뉴의 활성 상태 초기화
        slides.forEach((slide, i) => {
            slide.style.display = i === index ? "block" : "none";
        });
        menuItems.forEach((item, i) => {
            if (i === index) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });
        currentIndex = index;
    }

    // 초기 슬라이드 설정
    changeSlide(currentIndex);

    // 메뉴 아이템 클릭 이벤트
    menuItems.forEach((item, index) => {
        item.addEventListener("click", () => {
            changeSlide(index);
        });
    });

    // 이전 버튼 클릭 이벤트
    prevButton.addEventListener("click", () => {
        currentIndex = (currentIndex > 0) ? currentIndex - 1 : slides.length - 1;
        changeSlide(currentIndex);
    });

    // 다음 버튼 클릭 이벤트
    nextButton.addEventListener("click", () => {
        currentIndex = (currentIndex < slides.length - 1) ? currentIndex + 1 : 0;
        changeSlide(currentIndex);
    });

    // 드래그 기능 추가 (슬라이딩)
    let startX;
    document.querySelector(".education-swiper-container").addEventListener("mousedown", (e) => {
        startX = e.clientX;
    });

    document.querySelector(".education-swiper-container").addEventListener("mouseup", (e) => {
        const endX = e.clientX;
        if (startX > endX + 50) {
            currentIndex = (currentIndex < slides.length - 1) ? currentIndex + 1 : 0;
            changeSlide(currentIndex);
        } else if (startX < endX - 50) {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : slides.length - 1;
            changeSlide(currentIndex);
        }
    });

    // 터치 이벤트 추가 (모바일 슬라이딩)
    document.querySelector(".education-swiper-container").addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
    });

    document.querySelector(".education-swiper-container").addEventListener("touchend", (e) => {
        const endX = e.changedTouches[0].clientX;
        if (startX > endX + 50) {
            currentIndex = (currentIndex < slides.length - 1) ? currentIndex + 1 : 0;
            changeSlide(currentIndex);
        } else if (startX < endX - 50) {
            currentIndex = (currentIndex > 0) ? currentIndex - 1 : slides.length - 1;
            changeSlide(currentIndex);
        }
    });
});

