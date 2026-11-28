/** Shared merch cart/checkout client — window.MerchCore (ES2017, no deps). */
(function () {
  "use strict";

  var DEFAULT_STRIPE_JS = "https://js.stripe.com/endive/stripe.js";

  function readConfig() {
    var el = document.getElementById("merch-config");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "{}");
    } catch (e) {
      console.error("[MerchCore] invalid merch-config JSON");
      return null;
    }
  }

  function money(cents) {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
      (Number(cents) || 0) / 100,
    );
  }

  function clampQty(n) {
    var q = Math.floor(Number(n) || 0);
    if (q < 1) return 0;
    return Math.min(99, q);
  }

  function pathMatches(pathname, target) {
    if (!target) return false;
    var a = String(pathname || "").replace(/\/+$/, "") || "/";
    var b = String(target || "").replace(/\/+$/, "") || "/";
    return a === b;
  }

  function isCheckoutFlowPath(cfg, pathname) {
    var p = pathname || window.location.pathname;
    return (
      pathMatches(p, cfg.paths && cfg.paths.cart) ||
      pathMatches(p, cfg.paths && cfg.paths.checkout) ||
      pathMatches(p, cfg.paths && cfg.paths.thanks)
    );
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        var val = attrs[key];
        if (val == null || val === false) return;
        if (key === "text") {
          node.textContent = String(val);
          return;
        }
        if (key === "className") {
          node.className = String(val);
          return;
        }
        if (key === "htmlFor") {
          node.htmlFor = String(val);
          return;
        }
        if (key.slice(0, 2) === "on" && typeof val === "function") {
          node.addEventListener(key.slice(2).toLowerCase(), val);
          return;
        }
        if (val === true) {
          node.setAttribute(key, "");
          return;
        }
        node.setAttribute(key, String(val));
      });
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (child) {
        if (child == null || child === false) return;
        if (typeof child === "string") node.appendChild(document.createTextNode(child));
        else node.appendChild(child);
      });
    }
    return node;
  }

  function createCartApi(storageKey) {
    function read() {
      try {
        var raw = localStorage.getItem(storageKey);
        if (!raw) return [];
        var parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) return [];
        return parsed
          .map(function (row) {
            return {
              id: String(row.id || "").trim(),
              qty: Math.floor(Number(row.qty) || 0),
            };
          })
          .filter(function (row) {
            return row.id && row.qty >= 1 && row.qty <= 99;
          });
      } catch (e) {
        return [];
      }
    }

    function write(items) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(items));
        window.dispatchEvent(new CustomEvent("merch:cart-change"));
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

    function add(id, qty) {
      id = String(id || "").trim();
      qty = clampQty(qty || 1);
      if (!id || qty < 1) return false;
      var items = read();
      var found = false;
      for (var i = 0; i < items.length; i++) {
        if (items[i].id === id) {
          items[i].qty = Math.min(99, items[i].qty + qty);
          found = true;
          break;
        }
      }
      if (!found) items.push({ id: id, qty: qty });
      return write(items);
    }

    function setQty(id, qty) {
      id = String(id || "").trim();
      qty = Math.floor(Number(qty) || 0);
      var items = read().filter(function (row) {
        if (row.id === id) {
          if (qty < 1) return false;
          row.qty = Math.min(99, qty);
        }
        return true;
      });
      return write(items);
    }

    function remove(id) {
      id = String(id || "").trim();
      return write(
        read().filter(function (row) {
          return row.id !== id;
        }),
      );
    }

    function clear() {
      return write([]);
    }

    return { read: read, add: add, setQty: setQty, remove: remove, clear: clear, count: count };
  }

  var cfg = null;
  var cart = null;
  var toastTimer = null;

  function showToast(messageNodes) {
    var existing = document.querySelector(".merch-toast");
    if (existing) existing.remove();
    var toast = el("div", { className: "merch-toast", role: "status", "aria-live": "polite" });
    if (Array.isArray(messageNodes)) {
      messageNodes.forEach(function (n) {
        toast.appendChild(typeof n === "string" ? document.createTextNode(n) : n);
      });
    } else {
      toast.textContent = String(messageNodes || "");
    }
    document.body.appendChild(toast);
    if (toastTimer) window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.remove();
    }, 3500);
  }

  function showSaveError() {
    showToast("Could not save your cart. Turn off private browsing and try again.");
  }

  function refreshBadges() {
    if (!cart) return;
    var n = cart.count();
    document.querySelectorAll("[data-merch-badge]").forEach(function (badge) {
      badge.textContent = String(n);
      badge.hidden = n < 1;
    });
    refreshPill();
  }

  function setHasPill(on) {
    document.body.classList.toggle("merch-has-pill", !!on);
  }

  function refreshPill() {
    if (!cfg || !cart) return;
    var pill = document.querySelector(".merch-pill");
    if (!cfg.pill || isCheckoutFlowPath(cfg)) {
      if (pill) pill.hidden = true;
      setHasPill(false);
      return;
    }
    var n = cart.count();
    if (n < 1) {
      if (pill) pill.hidden = true;
      setHasPill(false);
      return;
    }
    if (!pill) {
      pill = el("a", {
        className: "merch-pill",
        href: (cfg.paths && cfg.paths.cart) || "/cart",
      });
      document.body.appendChild(pill);
    }
    pill.href = (cfg.paths && cfg.paths.cart) || "/cart";
    pill.textContent = "Cart (" + n + ") →";
    pill.hidden = false;
    setHasPill(true);
  }

  function wireAddForms() {
    document.querySelectorAll("form[data-merch-add]").forEach(function (form) {
      if (form.getAttribute("data-merch-wired") === "1") return;
      form.setAttribute("data-merch-wired", "1");
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var fd = new FormData(form);
        var id = String(fd.get("id") || "").trim();
        var qty = clampQty(fd.get("qty") || 1);
        if (!id || qty < 1) return;
        var ok = cart.add(id, qty);
        if (!ok) {
          showSaveError();
          return;
        }
        var btn = form.querySelector('button[type="submit"]');
        if (btn) {
          var prev = btn.textContent;
          btn.textContent = "Added ✓";
          window.setTimeout(function () {
            btn.textContent = prev;
          }, 1500);
        }
        var cartPath = (cfg.paths && cfg.paths.cart) || "/cart";
        showToast([
          "Added. ",
          el("a", { href: cartPath, text: "View cart" }),
        ]);
        refreshBadges();
      });
    });
  }

  function quoteCart() {
    return fetch(cfg.endpoints.quote, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: cart.read() }),
    }).then(function (res) {
      return res.json().catch(function () {
        return {};
      }).then(function (data) {
        return { res: res, data: data };
      });
    });
  }

  function mountCart(root) {
    var quoteSeq = 0;
    var debounceTimers = {};
    var built = false;
    var lineEls = {};
    var totalsEl = null;
    var actionsEl = null;
    var errorEl = null;
    var noteEl = null;

    function emptyState() {
      root.replaceChildren();
      root.appendChild(el("p", { className: "merch-empty merch-lede", text: "Your cart is empty." }));
      root.appendChild(
        el("div", { className: "merch-actions" }, [
          el("a", {
            className: "merch-btn merch-btn-primary",
            href: (cfg.paths && cfg.paths.shop) || "/",
            text: "Browse merch",
          }),
        ]),
      );
      built = false;
      lineEls = {};
      totalsEl = null;
      actionsEl = null;
    }

    function patchTotals(cartData) {
      if (!totalsEl) return;
      totalsEl.replaceChildren();
      totalsEl.appendChild(document.createTextNode("Subtotal " + money(cartData.subtotal_cents)));
      totalsEl.appendChild(el("br"));
      totalsEl.appendChild(document.createTextNode("Shipping " + money(cartData.shipping_cents)));
      if (cartData.shipping_cents === 0 && cartData.subtotal_cents > 0) {
        totalsEl.appendChild(document.createTextNode(" "));
        var note =
          cfg.freeShippingNote ||
          (cartData.free_ship_cents
            ? "(free over " + money(cartData.free_ship_cents) + ")"
            : "(free shipping)");
        totalsEl.appendChild(el("span", { className: "merch-muted", text: note }));
      }
      totalsEl.appendChild(el("br"));
      totalsEl.appendChild(el("strong", { text: "Total " + money(cartData.total_cents) }));
    }

    function ensureScaffold() {
      if (built) return;
      root.replaceChildren();
      var list = el("ul", { className: "merch-lines" });
      root.appendChild(list);
      noteEl = el("p", { className: "merch-note", hidden: true });
      root.appendChild(noteEl);
      totalsEl = el("p", { className: "merch-totals" });
      root.appendChild(totalsEl);
      errorEl = el("p", { className: "merch-inline-error", hidden: true });
      root.appendChild(errorEl);
      actionsEl = el("div", { className: "merch-actions" }, [
        el("a", {
          className: "merch-btn merch-btn-primary",
          href: (cfg.paths && cfg.paths.checkout) || "/checkout",
          text: "Checkout",
        }),
        el("a", {
          className: "merch-btn merch-btn-ghost",
          href: (cfg.paths && cfg.paths.shop) || "/",
          text: "Keep shopping",
        }),
      ]);
      root.appendChild(actionsEl);
      built = true;
      lineEls = {};
      root._merchList = list;
    }

    function bindQty(input, id) {
      var apply = function () {
        var raw = input.value;
        if (raw === "") return;
        var q = clampQty(raw);
        if (q < 1) {
          cart.remove(id);
          removeLineOptimistic(id);
          refresh();
          return;
        }
        input.value = String(q);
        cart.setQty(id, q);
        refresh();
      };
      input.addEventListener("input", function () {
        if (debounceTimers[id]) window.clearTimeout(debounceTimers[id]);
        debounceTimers[id] = window.setTimeout(apply, 300);
      });
      input.addEventListener("change", apply);
      input.addEventListener("blur", function () {
        if (input.value === "" || clampQty(input.value) < 1) {
          cart.remove(id);
          removeLineOptimistic(id);
          refresh();
        } else {
          apply();
        }
      });
    }

    function removeLineOptimistic(id) {
      var row = lineEls[id];
      if (row && row.parentNode) row.parentNode.removeChild(row);
      delete lineEls[id];
    }

    function upsertLine(item) {
      var list = root._merchList;
      var existing = lineEls[item.id];
      if (existing) {
        var price = existing.querySelector(".merch-line-price");
        if (price) price.textContent = money(item.line_cents);
        var qtyInput = existing.querySelector(".merch-qty");
        if (qtyInput && document.activeElement !== qtyInput) {
          qtyInput.value = String(item.qty);
        }
        return;
      }
      var qtyId = "merch-qty-" + String(item.id).replace(/[^a-zA-Z0-9_-]/g, "_");
      var qtyInput = el("input", {
        className: "merch-qty",
        type: "number",
        min: "1",
        max: "99",
        value: String(item.qty),
        id: qtyId,
        "data-merch-id": item.id,
        "aria-label": "Quantity",
      });
      bindQty(qtyInput, item.id);
      var removeBtn = el("button", {
        className: "merch-remove",
        type: "button",
        text: "Remove",
        "data-merch-id": item.id,
      });
      removeBtn.addEventListener("click", function () {
        cart.remove(item.id);
        removeLineOptimistic(item.id);
        refresh();
      });
      var li = el("li", { className: "merch-line", "data-merch-id": item.id }, [
        el("div", null, [
          el("div", null, [
            el("span", { className: "merch-line-title", text: item.title }),
            document.createTextNode(" "),
            el("span", { className: "merch-line-label", text: "(" + item.label + ")" }),
          ]),
          el("div", { className: "merch-line-meta" }, [
            el("label", { htmlFor: qtyId }, ["Qty ", qtyInput]),
            removeBtn,
          ]),
        ]),
        el("span", { className: "merch-line-price", text: money(item.line_cents) }),
      ]);
      list.appendChild(li);
      lineEls[item.id] = li;
    }

    function showError(msg) {
      if (!errorEl) return;
      if (!msg) {
        errorEl.hidden = true;
        errorEl.textContent = "";
        return;
      }
      errorEl.hidden = false;
      errorEl.textContent = msg;
    }

    function refresh() {
      var items = cart.read();
      if (!items.length) {
        emptyState();
        return;
      }
      ensureScaffold();
      var seq = ++quoteSeq;
      quoteCart()
        .then(function (result) {
          if (seq !== quoteSeq) return;
          var res = result.res;
          var data = result.data;
          if (!res.ok || !data.ok) {
            var err = (data && data.error) || "Could not price cart.";
            if (res.status === 400 && /unknown product/i.test(err)) {
              var match = err.match(/Unknown product:\s*(.+)$/i);
              if (match) {
                cart.remove(match[1].trim());
                removeLineOptimistic(match[1].trim());
                if (noteEl) {
                  noteEl.hidden = false;
                  noteEl.textContent = "Removed unavailable item from your cart.";
                }
                refresh();
                return;
              }
            }
            showError(err);
            return;
          }
          showError("");
          var seen = {};
          data.cart.items.forEach(function (item) {
            seen[item.id] = true;
            upsertLine(item);
          });
          Object.keys(lineEls).forEach(function (id) {
            if (!seen[id]) removeLineOptimistic(id);
          });
          patchTotals(data.cart);
        })
        .catch(function () {
          if (seq !== quoteSeq) return;
          showError("Could not price cart.");
        });
    }

    refresh();
  }

  function loadStripeJs(url) {
    return new Promise(function (resolve, reject) {
      if (typeof window.Stripe === "function") {
        resolve(window.Stripe);
        return;
      }
      var s = document.createElement("script");
      s.src = url || DEFAULT_STRIPE_JS;
      s.async = true;
      s.onload = function () {
        if (typeof window.Stripe === "function") resolve(window.Stripe);
        else reject(new Error("Stripe.js failed to load."));
      };
      s.onerror = function () {
        reject(new Error("Stripe.js failed to load."));
      };
      document.head.appendChild(s);
    });
  }

  function mountCheckout(root) {
    root.replaceChildren();
    root.classList.add("merch-checkout");
    var summary = el("div", { className: "merch-summary" });
    var errorEl = el("p", { className: "merch-error", hidden: true });
    var mount = el("div", { id: "merch-checkout-mount", className: "merch-checkout-mount" });
    root.appendChild(summary);
    root.appendChild(errorEl);
    root.appendChild(mount);

    function showError(msg) {
      errorEl.hidden = !msg;
      errorEl.textContent = msg || "";
    }

    function soon() {
      mount.hidden = true;
      summary.replaceChildren(
        el("p", {
          className: "merch-lede",
          text: "Checkout opening soon. Payments are not connected yet.",
        }),
        el("div", { className: "merch-actions" }, [
          el("a", {
            className: "merch-btn merch-btn-ghost",
            href: (cfg.paths && cfg.paths.cart) || "/cart",
            text: "Back to cart",
          }),
        ]),
      );
    }

    var items = cart.read();
    if (!items.length) {
      summary.appendChild(el("p", { className: "merch-lede", text: "Your cart is empty." }));
      summary.appendChild(
        el("div", { className: "merch-actions" }, [
          el("a", {
            className: "merch-btn merch-btn-primary",
            href: (cfg.paths && cfg.paths.shop) || "/",
            text: "Browse merch",
          }),
        ]),
      );
      mount.hidden = true;
      return;
    }

    summary.appendChild(el("p", { className: "merch-lede", text: "Loading cart…" }));
    var sessionId = null;

    quoteCart()
      .then(function (result) {
        if (!result.res.ok || !result.data.ok) {
          summary.replaceChildren(
            el("p", {
              className: "merch-lede",
              text: (result.data && result.data.error) || "Could not price cart.",
            }),
          );
          mount.hidden = true;
          return null;
        }
        var cartData = result.data.cart;
        var list = el("ul", { className: "merch-summary-list" });
        cartData.items.forEach(function (item) {
          list.appendChild(
            el("li", null, [
              el("span", null, [
                el("strong", { text: item.title }),
                document.createTextNode(" (" + item.label + ") × " + item.qty),
              ]),
              el("span", { text: money(item.line_cents) }),
            ]),
          );
        });
        summary.replaceChildren(
          list,
          el("p", null, [
            document.createTextNode("Subtotal " + money(cartData.subtotal_cents)),
            el("br"),
            document.createTextNode("Shipping " + money(cartData.shipping_cents)),
            el("br"),
            el("strong", { text: "Total " + money(cartData.total_cents) }),
          ]),
          el("p", null, [
            el("a", {
              href: (cfg.paths && cfg.paths.cart) || "/cart",
              text: "Edit cart",
            }),
          ]),
        );
        return true;
      })
      .then(function (ok) {
        if (!ok) return;
        var keyPromise = cfg.publishableKey
          ? Promise.resolve(cfg.publishableKey)
          : fetch(cfg.endpoints.config)
              .then(function (r) {
                return r.json().catch(function () {
                  return {};
                });
              })
              .then(function (data) {
                return data.publishableKey || null;
              });
        return keyPromise.then(function (pk) {
          if (!pk) {
            soon();
            return;
          }
          return loadStripeJs(cfg.stripeJsUrl || DEFAULT_STRIPE_JS).then(function (Stripe) {
            var stripe = Stripe(pk);
            function fetchClientSecret() {
              return fetch(cfg.endpoints.checkout, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ items: cart.read() }),
              }).then(function (res) {
                return res.json().catch(function () {
                  return {};
                }).then(function (data) {
                  if (res.status === 503) {
                    soon();
                    throw new Error(
                      data.error || "Checkout opening soon. Payments are not connected yet.",
                    );
                  }
                  if (!res.ok || !data.clientSecret) {
                    throw new Error(data.error || "Checkout failed.");
                  }
                  sessionId = data.id || null;
                  return data.clientSecret;
                });
              });
            }
            function onComplete() {
              var dest = (cfg.paths && cfg.paths.thanks) || "/thanks";
              if (sessionId) {
                dest +=
                  (dest.indexOf("?") >= 0 ? "&" : "?") +
                  "session_id=" +
                  encodeURIComponent(sessionId);
              }
              window.location.href = dest;
            }
            var starter =
              typeof stripe.createEmbeddedCheckoutPage === "function"
                ? stripe.createEmbeddedCheckoutPage.bind(stripe)
                : typeof stripe.initEmbeddedCheckout === "function"
                  ? stripe.initEmbeddedCheckout.bind(stripe)
                  : null;
            if (!starter) {
              throw new Error("Embedded Checkout is not available in this Stripe.js build.");
            }
            return starter({
              fetchClientSecret: fetchClientSecret,
              onComplete: onComplete,
            }).then(function (checkout) {
              checkout.mount("#merch-checkout-mount");
            });
          });
        });
      })
      .catch(function (err) {
        showError(err && err.message ? err.message : "Checkout failed.");
      });
  }

  function mountThanks(root) {
    root.replaceChildren();
    root.classList.add("merch-thanks");
    root.appendChild(el("h1", { text: "Checking payment…" }));
    root.appendChild(el("p", { className: "merch-lede", text: "One moment." }));

    var params = new URLSearchParams(window.location.search);
    var sessionId = (params.get("session_id") || "").trim();
    if (!sessionId) {
      root.replaceChildren(
        el("h1", { text: "Payment not completed" }),
        el("p", { className: "merch-lede", text: "No checkout session was found." }),
        el("div", { className: "merch-actions" }, [
          el("a", {
            className: "merch-btn merch-btn-primary",
            href: (cfg.paths && cfg.paths.checkout) || "/checkout",
            text: "Back to checkout",
          }),
        ]),
      );
      return;
    }

    var url =
      cfg.endpoints.sessionStatus +
      (cfg.endpoints.sessionStatus.indexOf("?") >= 0 ? "&" : "?") +
      "session_id=" +
      encodeURIComponent(sessionId);

    fetch(url)
      .then(function (res) {
        return res.json().catch(function () {
          return {};
        }).then(function (data) {
          return { res: res, data: data };
        });
      })
      .then(function (result) {
        var data = result.data;
        if (!result.res.ok || !data.ok) {
          root.replaceChildren(
            el("h1", { text: "Could not confirm payment" }),
            el("p", {
              className: "merch-lede",
              text: data.error || "Try again from checkout.",
            }),
            el("div", { className: "merch-actions" }, [
              el("a", {
                className: "merch-btn merch-btn-primary",
                href: (cfg.paths && cfg.paths.checkout) || "/checkout",
                text: "Back to checkout",
              }),
            ]),
          );
          return;
        }

        if (data.status === "complete" || data.paymentStatus === "paid") {
          cart.clear();
          refreshBadges();
          var summaryKids = [];
          if (data.items && data.items.length) {
            var list = el("ul", { className: "merch-summary-list" });
            data.items.forEach(function (item) {
              list.appendChild(
                el("li", null, [
                  el("span", {
                    text:
                      item.title +
                      (item.label ? " (" + item.label + ")" : "") +
                      " × " +
                      item.qty,
                  }),
                  el("span", {
                    text: item.line_cents != null ? money(item.line_cents) : "",
                  }),
                ]),
              );
            });
            summaryKids.push(list);
          }
          summaryKids.push(
            el("p", null, [
              document.createTextNode(
                "Shipping " +
                  (data.shipping_cents != null ? money(data.shipping_cents) : "—"),
              ),
              el("br"),
              el("strong", {
                text:
                  "Total " +
                  (data.amount_total_cents != null ? money(data.amount_total_cents) : "—"),
              }),
            ]),
          );
          root.replaceChildren(
            el("h1", { text: "Order confirmed" }),
            el("p", {
              className: "merch-lede",
              text:
                "Thanks" +
                (data.email ? ". We emailed " + data.email + " a receipt when mail is connected." : "."),
            }),
            el("div", { className: "merch-totals" }, summaryKids),
            el("div", { className: "merch-actions" }, [
              el("a", {
                className: "merch-btn merch-btn-primary",
                href: (cfg.paths && cfg.paths.shop) || "/",
                text: "Back to shop",
              }),
            ]),
          );
          return;
        }

        if (data.status === "open") {
          root.replaceChildren(
            el("h1", { text: "Payment not completed" }),
            el("p", {
              className: "merch-lede",
              text: "Your checkout session is still open.",
            }),
            el("div", { className: "merch-actions" }, [
              el("a", {
                className: "merch-btn merch-btn-primary",
                href: (cfg.paths && cfg.paths.checkout) || "/checkout",
                text: "Back to checkout",
              }),
            ]),
          );
          return;
        }

        root.replaceChildren(
          el("h1", { text: "Payment status: " + (data.status || "unknown") }),
          el("p", {
            className: "merch-lede",
            text: "If you were charged, contact the shop with your receipt.",
          }),
          el("div", { className: "merch-actions" }, [
            el("a", {
              className: "merch-btn merch-btn-ghost",
              href: (cfg.paths && cfg.paths.shop) || "/",
              text: "Back to shop",
            }),
          ]),
        );
      })
      .catch(function () {
        root.replaceChildren(
          el("h1", { text: "Could not confirm payment" }),
          el("p", { className: "merch-lede", text: "Network error. Try again." }),
          el("div", { className: "merch-actions" }, [
            el("a", {
              className: "merch-btn merch-btn-primary",
              href: (cfg.paths && cfg.paths.checkout) || "/checkout",
              text: "Back to checkout",
            }),
          ]),
        );
      });
  }

  function mountAll() {
    document.querySelectorAll("[data-merch-mount]").forEach(function (node) {
      var kind = node.getAttribute("data-merch-mount");
      if (kind === "cart") mountCart(node);
      else if (kind === "checkout") mountCheckout(node);
      else if (kind === "thanks") mountThanks(node);
    });
  }

  function init() {
    cfg = readConfig();
    if (!cfg || !cfg.storageKey) {
      console.error("[MerchCore] missing #merch-config");
      return;
    }
    cart = createCartApi(cfg.storageKey);
    window.MerchCore.cart = cart;
    wireAddForms();
    refreshBadges();
    mountAll();
    window.addEventListener("merch:cart-change", refreshBadges);
    window.addEventListener("storage", function (e) {
      if (e.key === cfg.storageKey) refreshBadges();
    });
  }

  window.MerchCore = {
    init: init,
    cart: null,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
