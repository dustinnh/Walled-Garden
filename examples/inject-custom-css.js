// Inject custom CSS for Authelia theme
(function() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = '/css/authelia-custom.css';
    document.head.appendChild(link);
})();
