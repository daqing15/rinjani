// tags combination count

m = function() {
	// http://snippets.dzone.com/posts/show/3545
	var combination = function(a) {
		var fn = function(n, src, got, all) {
			if (n == 0) {
				if (got.length > 0) {
					all[all.length] = got;
				}
				return;
			}
			for ( var j = 0; j < src.length; j++) {
				fn(n - 1, src.slice(j + 1), got.concat( [ src[j] ]), all);
			}
			return;
		}

		var all = [];
		for ( var i = 0; i < a.length; i++) {
			fn(i, a, [], all);
		}
		all.push(a);
		return all;
	}
	c = combination(this.tags.sort());
	if (c.length == 1 && c[0].length == 0) {
		emit('untagged', {tags: c, count: 1});
	} else {
		c.forEach(function(z) {
			emit(z.join('#'), {tags: z, count: 1});
		});
	}
};

r = function(key, values) {
	var total = 0;
	for ( var i = 0; i < values.length; i++) {
		total += values[i]['count'];
	}
	return {tags: values[0]['tags'], count: total}
};

['contents', 'users'].forEach(function(col) {
	collection_name = col.slice(0,-1)+ '_tag_combinations'
	res = db.runCommand( {
		mapreduce : col,
		map : m,
		reduce : r,
		query : {},
		out : collection_name
	});
	print(tojson(res));
});

