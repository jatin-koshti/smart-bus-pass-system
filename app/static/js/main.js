document.addEventListener('DOMContentLoaded', function () {
    // Seat Selector Logic
    const seatItems = document.querySelectorAll('.seat-item:not(.occupied)');
    const selectedSeatInput = document.getElementById('selected_seat_input');
    const displaySelectedSeat = document.getElementById('display_selected_seat');
    const submitBtn = document.getElementById('proceed_booking_btn');

    seatItems.forEach(seat => {
        seat.addEventListener('click', function () {
            seatItems.forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            const seatNum = this.getAttribute('data-seat');
            
            if (selectedSeatInput) {
                selectedSeatInput.value = seatNum;
            }
            if (displaySelectedSeat) {
                displaySelectedSeat.textContent = seatNum;
            }
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        });
    });
});
