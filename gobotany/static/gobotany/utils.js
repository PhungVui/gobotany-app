dojo.provide('gobotany.utils');


// notify()
// display a notification message at the top of the script
// that will eventually fade away
gobotany.utils.notify = function(txt) {
    var holder = dojo.byId('notification-msg');
    if (holder === null) {
        holder = dojo.place('<div class="hidden" id="notification-msg"></div>',
                            dojo.body());
    }

    holder.innerHTML = txt;

    var wbox = dojo.window.getBox();
    var holderbox = dojo.position(holder);

    var left = (wbox.w / 2) - (holderbox.w / 2);
    var top = wbox.t;
    dojo.style(holder,
               {position: 'absolute',
                top: top + 'px',
                left: left + 'px'});

    dojo.removeClass(holder, 'hidden');
    dojo.fadeIn({node: holder, duration: 1}).play();

    setTimeout(function() {
        dojo.fadeOut({node: holder}).play();
    }, 5000);
};

gobotany.utils.animate_changed = function(node) {
    var nodes = node;
    if (nodes.length === undefined)
        nodes = [nodes];

    setTimeout(function() {
        for (var x = 0; x < nodes.length; x++)
            dojo.anim(nodes[x], {backgroundColor: 'white'});
    }, 2000);
};

gobotany.utils.clone = function(obj, updated_args) {
    var new_obj = (obj instanceof Array) ? [] : {};
    for (i in obj) {
        new_obj[i] = obj[i]
    }

    if (updated_args !== undefined) {
        for (var x in updated_args)
            if (updated_args.hasOwnProperty(x))
                new_obj[x] = updated_args[x];
    }

    return new_obj;
};
