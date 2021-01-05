$(document).ready(function() {
	$("#ingredients_section").on("change", "input", function() {
		var pattern = new RegExp(/^(ingredients-\d+-)(ing_name)/);
		var id = $(this).attr('id');
		if (pattern.test(id)) {
			var ing_name = $(this).val();
			if (Object.keys(ings).includes(ing_name)) {
				var match = pattern.exec(id);
				var unit = ings[ing_name].unit;
				var category = ings[ing_name].category;
				var unit_element = '#' + match[1] + 'unit';
				var category_element = '#' + match[1] + 'category';
				$(unit_element).val(unit);
				$(category_element).val(category);
			}
		}
	});
});
