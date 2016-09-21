var handleClick = function() {
    var $column = $(this);
    var sortBy = $column.data().sortBy;
    var sortOrder = $column.data().sortOrder;
};

var setForm = function() {};

var setSortBy = function() {};

var toggleIcons = function() {};



$(document).ready(function () {
    $('.sortable-header').click(handleClick);
        function() {
        var sortBy = $(this).data().sortBy;
        document.getElementById('sort_by').value = sortBy;
        $('form[name=advanced_search]').trigger('submit');
    });