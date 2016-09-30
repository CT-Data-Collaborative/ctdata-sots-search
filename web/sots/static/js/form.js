// update text within limitation section
(function () {
    function setLimitText(val, target) {
        if (val === 'business_name') {
            var update_val = 'Narrow search by address';
        } else if (val === 'place_of_business_address') {
            var update_val = 'Narrow search by business name';
        } else {
            var update_val = '';
        }
        $(target).html(update_val);
    }

// toggle visibility of search limitation section
    function setVisibility(val, target) {
        if (val === 'business_name' || val === 'place_of_business_address') {
            $(target).removeClass('hidden')
        } else {
            $(target).addClass('hidden')
        }
    }

    function clearLimitText() {
        $('input#query_limit').val('');
    }

    function resetLimitButton() {
        $('#limit-button').removeClass('fa-minus-circle').addClass('fa-plus-circle');
        $('#limit-by-field').addClass('hidden');
    }

    function toggleLimitButton(selection) {
        if ($(selection).hasClass('fa-plus-circle')) {
            $(selection).removeClass('fa-plus-circle').addClass('fa-minus-circle');
            $('#limit-by-field').removeClass('hidden');
        } else {
            $(selection).addClass('fa-plus-circle').removeClass('fa-minus-circle');
            $('#limit-by-field').addClass('hidden');
        }
    }

    function parseIndexChoice() {
        var selected_index = $('#index_field').val();
        setLimitText(selected_index, '#search-limit');
        setVisibility(selected_index, '#limit-tweaks');
        // clearLimitText();
        resetLimitButton();
    }

    function pageInit() {
        var currentLimitValue = $('input#query_limit').val('');
        if (currentLimitValue.length > 0) {
            toggleLimitButton()
        }
    }
    $('#index_field').change(function () {
        parseIndexChoice();
    });

    $('#limit-button').click(function () {
        toggleLimitButton(this);
    });
    pageInit();
    $('[data-toggle="tooltip"]').tooltip();
})();
