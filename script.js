document.querySelectorAll('.role').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.role').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
    });
  });
  