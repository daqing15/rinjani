// map-reduce tags of Article/Activity
m = function() {
    this.tags.forEach( function(z) {
        emit(z, 1);
    }
  );
};

r = function(key, values) {
    var total = 0;
    for (var i=0; i < values.length; i++) {
        total += values[i];
    }
    return total
};


var tagCols = ['articles', 'activities', 'users'];
output = []
db.tags_.drop();
tagCols.forEach(function(col) {
	var res = db.runCommand( { mapreduce: col, map: m, reduce: r, query: {}, out: col+'_tags' });
	printjson(res);
	var cur = db[res.result].find();
	cur.forEach(function(x) {
		p = db.tags_.findOne({_id: x._id});
		if (!p) {
			db.tags_.save({_id: x._id, count: x.value });
		} else {
			p.count += x.value;
			db.tags_.save(p);
		};
	});
});
db.tags.drop();
db.tags_.renameCollection('tags')

