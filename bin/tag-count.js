// tag count

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


['contents', 'users'].forEach(function(col) {
    res = db.runCommand( { mapreduce: col, map: m, reduce: r, query: {}, out: col.slice(0,-1)+'_tags' });
    print(tojson(res));
});

