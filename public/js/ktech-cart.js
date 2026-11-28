/** Client cart helpers — localStorage key ktech_cart_v1. */
(function () {
  var KEY = "ktech_cart_v1";

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed
        .map(function (row) {
          return {
            slug: String(row.slug || "").trim(),
            size: String(row.size || "").trim(),
            qty: Math.floor(Number(row.qty) || 0),
          };
        })
        .filter(function (row) {
          return row.slug && row.size && row.qty >= 1 && row.qty <= 99;
        });
    } catch (e) {
      return [];
    }
  }

  function write(items) {
    try {
      localStorage.setItem(KEY, JSON.stringify(items));
      window.dispatchEvent(new CustomEvent("ktech-cart-change"));
      return true;
    } catch (e) {
      return false;
    }
  }

  function count() {
    return read().reduce(function (sum, row) {
      return sum + row.qty;
    }, 0);
  }

  function add(slug, size, qty) {
    qty = Math.min(99, Math.max(1, Math.floor(Number(qty) || 1)));
    var items = read();
    var found = false;
    for (var i = 0; i < items.length; i++) {
      if (items[i].slug === slug && items[i].size === size) {
        items[i].qty = Math.min(99, items[i].qty + qty);
        found = true;
        break;
      }
    }
    if (!found) items.push({ slug: slug, size: size, qty: qty });
    return write(items);
  }

  function setQty(slug, size, qty) {
    qty = Math.floor(Number(qty) || 0);
    var items = read().filter(function (row) {
      if (row.slug === slug && row.size === size) {
        if (qty < 1) return false;
        row.qty = Math.min(99, qty);
      }
      return true;
    });
    return write(items);
  }

  function remove(slug, size) {
    return write(
      read().filter(function (row) {
        return !(row.slug === slug && row.size === size);
      }),
    );
  }

  function clear() {
    return write([]);
  }

  window.KtechCart = {
    KEY: KEY,
    read: read,
    write: write,
    count: count,
    add: add,
    setQty: setQty,
    remove: remove,
    clear: clear,
  };
})();
