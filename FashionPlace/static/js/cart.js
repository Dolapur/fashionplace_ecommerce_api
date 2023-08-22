
 function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
      }
      const csrftoken = getCookie('csrftoken');



let btns = document.getElementsByClassName('addtocart');
for (let i = 0; i < btns.length; i++) {
  btns[i].addEventListener('click', function(e) {
    let product_id = e.target.dataset.product;
    let action = e.target.dataset.action;
    console.log(product_id);
    if (user === 'AnonymousUser') {
      console.log('AnonymousUser');
      updateCart(product_id, action);
      location.reload();
    } else {
      updateCart(product_id, action);
      location.reload();
      
    }
  });
}

function updateCart(p_id, act) {
  const data = { product_id: p_id, action: act };

  let url = '/updatecart';
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      document.getElementById('cart').innerHTML = data.quantity; // Update cart quantity
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

let inputfields = document.getElementsByTagName('input');
for (let i = 0; i < inputfields.length; i++) {
  inputfields[i].addEventListener('change', updateQuantity);
}

function updateQuantity(e) {
  let inputvalue = e.target.value;
  let product_id = e.target.dataset.product;

  const data = { p_id: product_id, in_val: inputvalue };
  let url = '/updatequantity';

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      e.target.parentElement.parentElement.children[4].innerHTML = `<h3>$${data.subtotal.toFixed(2)}</h3>`;
      document.getElementById('total').innerHTML = `<h3><strong>$${data.grandtotal.toFixed(2)}</strong></h3>`;
      document.getElementById('cart').innerHTML = data.quantity; // Update cart quantity
      location.reload();  // Reload the page immediately
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}
