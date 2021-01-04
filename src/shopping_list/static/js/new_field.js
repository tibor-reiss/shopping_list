$(function(){
    $("#ingredients_section").on("change", "input", function(){
        var allFieldsFilled = true;
        var numberOfFields = 0;
        $("#ingredients_section").children('input').each(function() {
            var pattern = new RegExp(/^ingredients-\d+-ing_name/);
            if (pattern.test($(this).attr('id'))) {
                numberOfFields++;
                if ($(this).val() == "") {
                    allFieldsFilled = false;
                }
            }
        });

        if (allFieldsFilled) {
            var field_ing_name = "<input type='text' size='15' name='ingredients-" + numberOfFields + "-ing_name' id='ingredients-" + numberOfFields + "-ing_name' />"
            var field_amount = "<input type='text' size='5' name='ingredients-" + numberOfFields + "-amount' id='ingredients-" + numberOfFields + "-amount' style='text-align: right' />"
            var field_unit = "<input type='text' size='5' name='ingredients-" + numberOfFields + "-unit' id='ingredients-" + numberOfFields + "-unit' />"
            var field_category = ''
            if ($(this).closest('form').attr('id') == "recipe_single" ) {
            	field_category = "<select name='ingredients-" + numberOfFields + "-category' id='ingredients-" + numberOfFields + "-category'><option value='fruit'>fruit</option><option value='vegetable'>vegetable</option><option value='spice'>spice</option><option value='meat'>meat</option><option value='bread'>bread</option><option value='dairy'>dairy</option><option value='exotic'>exotic</option><option value='side_dish'>side_dish</option><option value='nut'>nut</option><option hidden disabled selected value></option></select>"
            }
            var new_input = field_ing_name + "\xa0" + field_amount + "\xa0" + field_unit + "\xa0" + field_category + "<br />";
            $(new_input).appendTo("#ingredients_section");
            
        }
    });
});