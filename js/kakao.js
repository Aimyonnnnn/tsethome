
window.onload = function () {
    // 모든 리스트 컨테이너와 메뉴 아이템을 선택
    const listContainers = document.querySelectorAll(".list-container");
    const menuItems = document.querySelectorAll(".education-menu-item");
    let currentIndex = 0;

    // 초기 상태 설정 함수
    function initializePage() {
        if (listContainers.length > 0 && menuItems.length > 0) {
            // 모든 리스트 컨테이너 숨기기, 첫 번째만 보이기
            listContainers.forEach((container, index) => {
                container.style.display = index === 0 ? "block" : "none";
            });
            // 모든 메뉴 아이템에서 active 클래스 제거하고 첫 번째 항목에만 추가
            menuItems.forEach(item => item.parentElement.classList.remove("active"));
            menuItems[0].parentElement.classList.add("active");
            console.log("페이지 초기화 완료"); // 초기화 확인용 로그
        } else {
            console.error("리스트 컨테이너나 메뉴 항목이 존재하지 않습니다.");
        }
    }

    initializePage(); // 페이지 초기화

    // 메뉴 아이템 이벤트 설정
    menuItems.forEach((item, index) => {
        item.addEventListener("click", () => showContainerByIndex(index));
        item.addEventListener("mouseenter", () => showContainerByIndex(index));
        item.addEventListener("touchstart", () => showContainerByIndex(index));
    });

    // 특정 컨테이너 보이기 함수
    function showContainerByIndex(index) {
        listContainers.forEach((container, i) => {
            container.style.display = i === index ? "block" : "none";
        });
        currentIndex = index;
        // 모든 메뉴 아이템에서 active 클래스 제거 후 현재 인덱스에 추가
        menuItems.forEach(item => item.parentElement.classList.remove("active"));
        menuItems[index].parentElement.classList.add("active");
    }

    // 드래그 및 터치 이벤트 처리
    let startX = 0;
    let isDragging = false;

    listContainers.forEach(container => {
        container.addEventListener("mousedown", (e) => {
            startX = e.clientX;
            isDragging = true;
        });

        container.addEventListener("mousemove", (e) => {
            if (!isDragging) return;
            const currentX = e.clientX;
            const difference = startX - currentX;
            if (Math.abs(difference) > 50) {
                if (difference > 0) showNext();
                else showPrevious();
                isDragging = false;
            }
        });

        container.addEventListener("mouseup", () => {
            isDragging = false;
        });

        container.addEventListener("touchstart", (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });

        container.addEventListener("touchmove", (e) => {
            if (!isDragging) return;
            const currentX = e.touches[0].clientX;
            const difference = startX - currentX;
            if (Math.abs(difference) > 50) {
                if (difference > 0) showNext();
                else showPrevious();
                isDragging = false;
            }
        });

        container.addEventListener("touchend", () => {
            isDragging = false;
        });
    });

    // 다음 컨테이너로 이동
    function showNext() {
        currentIndex = (currentIndex + 1) % listContainers.length;
        updateContainerDisplay();
    }

    // 이전 컨테이너로 이동
    function showPrevious() {
        currentIndex = (currentIndex - 1 + listContainers.length) % listContainers.length;
        updateContainerDisplay();
    }

    // 컨테이너 및 메뉴 아이템 업데이트
    function updateContainerDisplay() {
        listContainers.forEach((container, index) => {
            container.style.display = index === currentIndex ? "block" : "none";
        });
        menuItems.forEach((item, index) => {
            item.parentElement.classList.toggle("active", index === currentIndex);
        });
    }
};
