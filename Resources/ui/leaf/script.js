let leaf = $(".leaf");

function createLeaf(color) {
  let newLeaf = document.createElement("div");
  newLeaf.setAttribute("class", "leaf");
  newLeaf.style.background = color;
  $(".container").append(newLeaf);
}

for (let i = 0; i <= 32; i++) {
  createLeaf("#F95A8D");
}

let allLeaf = Array.from($(".container").find(".leaf"));

allLeaf.forEach((leaf, index) => {
  var tl = new TimelineMax({});
  index += 2;
  var rotation = 10.5 * index;
  tl.to(leaf, 7, {rotation: rotation + "deg",opacity: 0.1,backgroundColor: "#704FFE"}).to(leaf, 6,{rotation: 0,backgroundColor: "#13E2BE"},"+=1"
    );
});
