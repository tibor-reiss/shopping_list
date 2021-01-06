$(document).ready(function() {
	$("#ingredients_section").on("change", "input", function() {
		var pattern = new RegExp(/^(ingredients-\d+-)(ing_name)/);
		var id = $(this).attr('id');
		if (pattern.test(id)) {
			var ing_name = $(this).val();
			stopProcessing = false;

			// Check if duplicate
			$("#ingredients_section").children('input').each(function() {
				console.log('START...');
				loop_id = $(this).attr('id');
				console.log(loop_id);
				if (pattern.test(loop_id)) {
					console.log(id, loop_id);
					if (id == loop_id) return;
					if ($(this).val() == ing_name) {
						alert('There is already a line with ' + ing_name + '!');
						$('#' + id).val('');
						stopProcessing = true;
					}
				}
			})
			if (stopProcessing) return;

			// Check if ingredient already exists in database
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
