const grid = document.getElementById("grid");
const status = document.getElementById("status");

async function loadProducts(){
  status.textContent = "Loading…";

  try{
    const res = await fetch("/api/products");
    const data = await res.json();

    if(!data.ok){
      status.textContent = "API not live yet (normal on first deploy).";
      return;
    }

    grid.innerHTML = data.items.map(p => `
      <div class="card">
        <h3>${p.name}</h3>
        <p>${p.short_desc}</p>
        <p><strong>$${(p.price_cents/100).toFixed(2)}</strong></p>
        <button class="btn accent">Add</button>
      </div>
    `).join("");

    status.textContent = `${data.items.length} products`;
  }catch{
    status.textContent = "API not connected yet.";
  }
}

loadProducts();
