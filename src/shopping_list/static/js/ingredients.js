$(document).ready(function() {
	$("#ingredients_section").on("change", "input", function() {
		var pattern = new RegExp(/^(ingredients-\d+-)(ing_name)/);
		var id = $(this).attr('id');
		if (pattern.test(id)) {
			var ing_name = $(this).val();
			var match = pattern.exec(id);
			var amount_element = '#' + match[1] + 'amount';
			var unit_element = '#' + match[1] + 'unit';
			var category_element = '#' + match[1] + 'category';
			$(amount_element).val('');
			if (Object.keys(ings).includes(ing_name)) {
				var unit = ings[ing_name].unit;
				var category = ings[ing_name].category;
				$(unit_element).val(unit);
				$(category_element).val(category);
			}
			else {
				$(unit_element).val('');
				$(category_element).val('');
			}
		}
	});
});
