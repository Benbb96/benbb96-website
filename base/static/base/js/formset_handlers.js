(function($) {
    // Add the event handler after a new row is added
    $(document).on('formset:added', function(event, $row, formsetName) {
        if (formsetName === 'avis_set') {
            $row.find('.uploadFirebaseImage').on('click', uploadImage);
        }
    });
})(django.jQuery);