document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // URL 파라미터에서 UTM 정보 추출
        const urlParams = new URLSearchParams(window.location.search);
        
        const formData = {
            current_carrier: document.querySelector('#current-provider').value,
            desired_carrier: document.querySelector('#desired-provider').value,
            desired_phone: document.querySelector('#desired-model').value,
            contact: document.querySelector('#contact-number').value,
            additional_notes: document.querySelector('#additional-request').value,
            referrer: document.referrer || 'direct',
            utm_source: urlParams.get('utm_source') || '',
            utm_medium: urlParams.get('utm_medium') || '',
            utm_campaign: urlParams.get('utm_campaign') || ''
        };

        // 기타 입력 처리
        if (formData.current_carrier === '기타') {
            formData.current_carrier = document.querySelector('#current-custom-input').value;
        }
        if (formData.desired_carrier === '기타') {
            formData.desired_carrier = document.querySelector('#desired-custom-input').value;
        }

        try {
            const response = await fetch('/api/submit-consultation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                alert('상담 신청이 완료되었습니다.');
                form.reset();
            } else {
                const errorData = await response.json();
                alert(`오류가 발생했습니다: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버 연결에 실패했습니다.');
        }
    });
});