// map-reduce tags of Article/Activity
m = function() {
    this.tags.forEach( function(z) {
        emit(z, { count: 1 });
    }
  );
};

r = function(key, values) {
    var total = 0;
    for (var i=0; i < values.length; i++) {
        total += values[i].count;
    }
    return { count: total }
};


var tagCols = ['articles', 'activities'];
output = []
db.tags.drop();
tagCols.forEach(function(col) {
	var res = db.runCommand( { mapreduce: col, map: m, reduce: r, query: {} });
	printjson(res);
	var cur = db[res.result].find();
	cur.forEach(function(x) {
		p = db.tags.findOne({_id: x._id});
		if (!p) {
			db.tags.save({_id: x._id, count: x.value.count });
		} else {
			p.count += x.value.count;
			db.tags.save(p);
		};
	});
	db[res.result].drop()
});

