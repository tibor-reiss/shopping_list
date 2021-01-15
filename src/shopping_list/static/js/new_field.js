function wrapper(callback) {
    return function check_fields() {
        var allFieldsFilled = true;
        var numberOfFields = 0;
        var form_id = $("#ingredients_section").closest('form').attr('id');
        $("#ingredients_section").children('input').each(function() {
            var pattern = new RegExp(/^ingredients-\d+-ing_name/);
            if (pattern.test($(this).attr('id'))) {
                numberOfFields++;
                if ($(this).val() == "") {
                    allFieldsFilled = false;
                }
            }
        })
        callback({ filled: allFieldsFilled, counter: numberOfFields, form_id: form_id });
    }
};

function add_field(result) {
    var fields = result.counter;
    if (result.filled) {
        var field_ing_name = "<input type='text' size='15' name='ingredients-" + fields + "-ing_name' id='ingredients-" + fields + "-ing_name'>"
        var field_amount = "<input type='text' size='5' name='ingredients-" + fields + "-amount' id='ingredients-" + fields + "-amount' style='text-align: right'>"
        var field_unit = "<input type='text' size='5' name='ingredients-" + fields + "-unit' id='ingredients-" + fields + "-unit'>"
        var field_category = ''
        if (result.form_id == "recipe_single" ) {
            field_category = "<select name='ingredients-" + fields + "-category' id='ingredients-" + fields + "-category'><option value='fruit'>fruit</option><option value='vegetable'>vegetable</option><option value='spice'>spice</option><option value='meat'>meat</option><option value='bread'>bread</option><option value='dairy'>dairy</option><option value='exotic'>exotic</option><option value='side_dish'>side_dish</option><option value='nut'>nut</option><option hidden disabled selected value></option></select>"
        }
        var new_input = field_ing_name + "\xa0" + field_amount + "\xa0" + field_unit + "\xa0" + field_category + "<br />";
        $(new_input).appendTo("#ingredients_section");                
    }
};

$(document).ready(wrapper(add_field));

$(document).ready(function(){
    $("#ingredients_section").on("change", "input", wrapper(add_field));
});
