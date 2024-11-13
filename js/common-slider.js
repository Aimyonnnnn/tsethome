// Main Slider Script


// New Background Slider Script

let bgCurrentIndex = 0;
const bgSlides = document.querySelectorAll('.newslider-wrapper .new-slide');
const bgTotalSlides = bgSlides.length;
const bgSlideWidth = 253 + 13; // Slide width + gap between slides
const bgSliderWrapper = document.querySelector('.newslider-wrapper');

// Duplicate slides to create seamless looping effect
bgSlides.forEach(slide => {
    const clone = slide.cloneNode(true);
    bgSliderWrapper.appendChild(clone);
});

function showNextBgSlide() {
    bgCurrentIndex++;
    bgSliderWrapper.style.transition = 'transform 1s ease-in-out';
    bgSliderWrapper.style.transform = `translateX(${-bgCurrentIndex * bgSlideWidth}px)`;

    if (bgCurrentIndex >= bgTotalSlides) {
        setTimeout(() => {
            bgSliderWrapper.style.transition = 'none'; // Disable transition
            bgCurrentIndex = 0; // Reset index
            bgSliderWrapper.style.transform = `translateX(0px)`; // Reset position
        }, 1000); // Match transition duration
    }
}


setInterval(showNextBgSlide, 2000); // 2-second interval for background slider
