(function(window, $) {
    var callback = function() {
        var calculation = {
            url: '/warehouse/product/',
            node: function($row) {
                var id = $('.product select', $row).val();

                $.getJSON(calculation.url + id + '/details', null, function(product) {
                    var custom_price = $('.custom_price input', $row).val();
                    var quantity_change = $('.quantity_change input', $row).val();

                    var price = custom_price || product.price;

                    $('.total_cost div', $row).html(price * quantity_change);
                    $('.currency div', $row).html(product.currency.slug);
                })
            }
        };

        $('.grp-table').on('change', '.quantity_change input', function() {
            $('.grp-table').trigger('django.admin.calculate_node', [ $(this).parents('.grp-tr') ])
        }).on('change', '.custom_price input', function() {
            $('.grp-table').trigger('django.admin.calculate_node', [ $(this).parents('.grp-tr') ])
        }).on('change', '.product select', function() {
            $('.grp-table').trigger('django.admin.calculate_node', [ $(this).parents('.grp-tr') ])
        }).on('django.admin.calculate_node', function(e, $row) {
            calculation.node($row);
        });
    };

    $(document).ready(callback)
})(window, django.jQuery);