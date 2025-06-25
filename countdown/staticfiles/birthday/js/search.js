document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const cards = document.querySelectorAll('.birthday-card');

    cards.forEach(card => {
      // Get the name from the h5 element inside the card
      const nameElement = card.querySelector('h5');
      const name = nameElement ? nameElement.textContent.toLowerCase() : '';
      
      if (name.includes(query)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  });

  // Trim whitespace and make search more flexible
  const normalizedQuery = query.trim().toLowerCase();

  // Check if query is empty
  if (!normalizedQuery) {
    card.style.display = 'block';
    return;
  }

  // More flexible matching
  if (name.includes(normalizedQuery) || 
      normalizedQuery.split(' ').some(term => name.includes(term))) {
    card.style.display = 'block';
  } else {
    card.style.display = 'none';
  }
});