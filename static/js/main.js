document.addEventListener('DOMContentLoaded', function() {
    // Theme switcher functionality
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    }

    function switchTheme(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }    
    }

    toggleSwitch.addEventListener('change', switchTheme, false);

    // Show/hide TBSA input based on calculation type
    const calcTypeInputs = document.querySelectorAll('input[name="calc_type"]');
    const tbsaInput = document.getElementById('burn_area_input');

    calcTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            tbsaInput.style.display = this.value === 'emergency' ? 'block' : 'none';
        });
    });

    // Form submission handling
    const form = document.querySelector('form');
    const burnAreaInput = document.getElementById('burn_area_input');
    const resultsSection = document.querySelector('.results-section');

    // Form validation
    form.addEventListener('submit', function(e) {
        const weightInput = document.getElementById('weight');
        const tbsaInput = document.getElementById('tbsa');
        const calcType = document.querySelector('input[name="calc_type"]:checked');

        if (!weightInput.value || isNaN(weightInput.value)) {
            e.preventDefault();
            alert('Please enter a valid weight');
            return;
        }

        if (calcType.value === 'emergency' && tbsaInput.style.display !== 'none') {
            if (!tbsaInput.value || isNaN(tbsaInput.value)) {
                e.preventDefault();
                alert('Please enter a valid TBSA percentage');
                return;
            }
        }
    });
});
