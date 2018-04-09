class TextminingController < ApplicationController
  skip_before_action :verify_authenticity_token

  def index
  end

  def transaction
    require "neo4j-core"

    # Session
    session = Neo4j::Session.open(:server_db)

    # Label/Index
    labels = %w(Text Geographic Organization Person Geopolitical Time Artifact Event Phenomenon)
    lshort = %w(txt geo org per gpe tim art eve nat)
    lshort2label = lshort.zip(labels).to_h

    labels.each do |label|
      Neo4j::Label.create(label).create_index(:name)
    end

    # Parse NER json
    ner_json = File.open("algorithms/Json.txt").each_line.map(&:to_s).join
    nj = JSON.parse(ner_json).to_a.reject { |i| i['word'].match?(/\A[`'"]+\z/) rescue true }

    Neo4j::Transaction.run do
      # Deletes all nodes
      all_nodes = Neo4j::Session.query("MATCH (n) RETURN n")
      all_nodes.each { |n| n.first.delete }

      this_news = Neo4j::Node.create({name: 'Text'}, 'Text')

      # Creates nodes and sets relations
      nj.each do |u|
        if lshort.include?(u['cate'])
          node = Neo4j::Node.create({name: u['word']}, lshort2label[u['cate']])
          this_news.create_rel(('has_' + u['cate']).to_sym, node)
        end
      end
    end
  end

  def submit_article # TODO: ban pushing the button before any procedure has finished
    File.open("algorithms/input.txt", "w") { |f| f.write(params[:article]) }
    `python3 algorithms/myNER2.py`
    `algorithms/query`
    transaction
    s = File.open("algorithms/resultWeight.txt").each_line.map(&:split).map { |s| s.join ?, } .join(?\n)
    File.open("public/flare.csv", 'w') { |f| f.write("id,value\n" + s) }
    respond_to do |f|
      f.json { render json: { statistics_html:
<<-'EOS',
<svg width="960" height="960" font-family="sans-serif" font-size="10" text-anchor="middle"></svg>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var format = d3.format(",d");

var color = d3.scaleOrdinal(d3.schemeCategory20c);

var pack = d3.pack()
    .size([width, height])
    .padding(1.5);

d3.csv("flare.csv", function(d) {
  d.value = +d.value;
  if (d.value) return d;
}, function(error, classes) {
  if (error) throw error;

  var root = d3.hierarchy({children: classes})
      .sum(function(d) { return d.value; })
      .each(function(d) {
        if (id = d.data.id) {
          var id, i = id.lastIndexOf(".");
          d.id = id;
          d.package = id.slice(0, i);
          d.class = id.slice(i + 1);
        }
      });

  var node = svg.selectAll(".node")
    .data(pack(root).leaves())
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

  node.append("circle")
      .attr("id", function(d) { return d.id; })
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) { return color(d.package); });

  node.append("clipPath")
      .attr("id", function(d) { return "clip-" + d.id; })
    .append("use")
      .attr("xlink:href", function(d) { return "#" + d.id; });

  node.append("text")
      .attr("clip-path", function(d) { return "url(#clip-" + d.id + ")"; })
    .selectAll("tspan")
    .data(function(d) { return d.class.split(/(?=[A-Z][^A-Z])/g); })
    .enter().append("tspan")
      .attr("x", 0)
      .attr("y", function(d, i, nodes) { return 13 + (i - nodes.length / 2 - 0.5) * 10; })
      .text(function(d) { return d; });

  node.append("title")
      .text(function(d) { return d.id + "\n" + format(d.value); });
});

</script>
EOS
tags_html:
<<-EOS
#{
n = File.open("algorithms/input.txt").each_line.map(&:to_s).join ?\n
s = File.open("algorithms/Json.txt").each_line.map(&:to_s).join
u = JSON.parse(s).to_a.reject { |i| i['word'].match?(/\A[`'"]+\z/) rescue true }

n_ptr, u_ptr = 0, 0
res = '<div class="entities">'
until n_ptr == n.size
  w = u[u_ptr]['word'] rescue nil
  if u_ptr < u.size && n[n_ptr, w.size] == w
    res += '<mark data-entity="' + u[u_ptr]['cate'] + '">' if u[u_ptr]['cate'] != 'None'
    res += w
    res += '</mark>' if u[u_ptr]['cate'] != 'None'
    n_ptr += w.size
    u_ptr += 1
  else
    res += n[n_ptr].force_encoding("ISO-8859-1").encode("UTF-8")
    n_ptr += 1
  end
end
res += '</div>'
}
EOS
        }
      }
    end
  end
end
