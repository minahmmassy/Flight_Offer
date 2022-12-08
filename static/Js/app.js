// Loader function
document.onreadystatechange = function () {
  if (document.readyState !== "complete") {
    document.body.style.visibility = "hidden";
    document.querySelector("#loader").style.visibility = "visible";
  } else {
    document.querySelector("#loader").style.display = "none";
    document.body.style.visibility = "visible";
  }
};

// owl carousel
$(document).ready(function () {
  $(".owl-carousel").owlCarousel({
    loop: true,
    margin: 15,
    nav: true,
    autoplay: true,
    autoplayTimeout: 2000,
    autoplayHoverPause: true,
    smartSpeed: 1000,
    responsive: {
      0: {
        items: 1,
      },
      600: {
        items: 3,
      },
      1000: {
        items: 4,
      },
    },
  });
});

// owl carousel custom nav
var owl = $(".owl-carousel");
owl.owlCarousel();
// Go to the next item
$(".next").click(function () {
  owl.trigger("next.owl.carousel");
});
// Go to the previous item
$(".prev").click(function () {
  // With optional speed parameter
  // Parameters has to be in square bracket '[]'
  owl.trigger("prev.owl.carousel", [300]);
});
