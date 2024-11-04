function showTab(tabId) {
    // Hide all tab panes
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
        pane.classList.remove('active');
    });

    // Remove active class from all tab links
    const tabLinks = document.querySelectorAll('.tab-link');
    tabLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Show the selected tab pane and activate the corresponding tab link
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`.tab-link[onclick="showTab('${tabId}')"]`).classList.add('active');
}

function addCommas(nStr) {
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
    x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2
}

window.onload = function() {
    const popupModal = document.getElementById("popupModal");
    if (!localStorage.getItem("popupShown")) {
      popupModal.style.display = "flex"; // Show modal in flex mode
      localStorage.setItem("popupShown", "true");
    }
  };
  
  // Close the popup when the user clicks the close button
  document.querySelector(".close-btn").onclick = function() {
    document.getElementById("popupModal").style.display = "none";
  };
  
  // Close the popup if the user clicks outside the content
  window.onclick = function(event) {
    const modal = document.getElementById("popupModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };

  