document.addEventListener('DOMContentLoaded', function () {
    const table = document.querySelector('table');
    const headers = table.querySelectorAll('th');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const columnIndex = header.cellIndex;
            const rows = Array.from(table.querySelectorAll('tbody tr'));

            // Remove the arrow from all headers
            headers.forEach(h => {
                if (h !== header) {
                    h.classList.remove('asc', 'desc');
                }
            });

            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();

                // Custom sorting logic for different data types
                if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
                    return parseFloat(aValue) - parseFloat(bValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });

            const isDescending = header.classList.toggle('desc');
            header.classList.toggle('asc', !isDescending);

            if (isDescending) {
                rows.reverse();
            }

            table.querySelector('tbody').append(...rows);
        });
    });
});
