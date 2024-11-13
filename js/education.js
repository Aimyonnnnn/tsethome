document.addEventListener("DOMContentLoaded", function () {
    // 메뉴 항목과 이미지 요소 가져오기
    const menuItems = document.querySelectorAll('.education-menu-item');
    const educationImage = document.getElementById('educationImage');

    // 이미지 경로 배열
    const imagePaths = [
        'img/41.svg', // 법정의무교육1
        'img/42.svg', // 법정의무교육2
        'img/43.svg', // 직무 교육
        'img/41.svg', // 소양 교육
        'img/42.png'  // 추천 행사
    ];

    // 메뉴 항목에 대한 클릭 이벤트 추가
    menuItems.forEach((item, index) => {
        item.addEventListener('click', function () {
            changeImage(index);
        });
    });

    // 이미지 변경 함수
    function changeImage(index) {
        // 선택된 index에 따라 이미지 변경
        educationImage.src = imagePaths[index];
    }
});
