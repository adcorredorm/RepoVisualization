const xAxisLabelText = 'Effective Lines';
const target_repo = 'lt-chat-ms';
const full_width = document.body.clientWidth;
const full_height = document.body.clientHeight;

const chart_width = full_width * 0.7;
const chart_height = full_height * 0.6;

const binfo_width = full_width;
const binfo_height = full_height - chart_height;

const sinfo_width = full_width - chart_width;
const sinfo_height = chart_height;
const textmargin = { x: 20, y: 20 };

const svg = d3
  .select('svg')
  .attr('width', full_width)
  .attr('height', full_height);

var lang_colors = {};

function colors(lang) {
  if (lang === undefined || lang === null) return 'black';
  if (lang in lang_colors) return lang_colors[lang].color;
  return 'black';
}

function render(data) {
  const data_org = data.org;
  delete data.org;
  data = data[target_repo];
  files_data = Object.values(data.files)
    .sort((a, b) => b.effective_lines - a.effective_lines)
    .slice(0, 25);

  const xValue = (d) => d.effective_lines;
  const yValue = (d) => d.name;
  const margin = { top: 40, right: 20, bottom: 20, left: 180 };
  const innerWidth = chart_width - margin.left - margin.right;
  const innerHeight = chart_height - margin.top - margin.bottom;

  const xScale = d3
    .scaleLinear()
    .domain([0, d3.max(files_data, xValue)])
    .range([0, innerWidth]);

  const yScale = d3
    .scaleBand()
    .domain(files_data.map(yValue))
    .range([0, innerHeight])
    .padding(0.1);

  const chart = svg
    .append('g')
    .attr('id', 'chart')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const xAxisTickFormat = (number) =>
    d3.format('.3s')(number).replace('G', 'B');

  const xAxis = d3
    .axisBottom(xScale)
    .tickFormat(xAxisTickFormat)
    .tickSize(-innerHeight);

  chart
    .append('g')
    .call(d3.axisLeft(yScale))
    .selectAll('.domain, .tick line')
    .remove();

  const xAxisG = chart
    .append('g')
    .call(xAxis)
    .attr('transform', `translate(0,${innerHeight})`);

  xAxisG.select('.domain').remove();

  xAxisG
    .append('text')
    .attr('class', 'axis-label')
    .attr('y', 40)
    .attr('x', innerWidth / 2)
    .attr('fill', 'black')
    .text(xAxisLabelText);

  chart
    .selectAll('rect')
    .data(files_data)
    .enter()
    .append('rect')
    .attr('y', (d) => yScale(yValue(d)))
    .attr('width', (d) => xScale(xValue(d)))
    .attr('height', yScale.bandwidth())
    .attr('fill', (d) => colors(d.language))
    .on('mouseover', mouseover)
    .on('mouseout', mouseout);

  chart
    .append('text')
    .attr('class', 'title')
    .attr('y', -margin.top / 2)
    .attr('x', (innerWidth - margin.left) / 2)
    .text(target_repo);

  const binfo = svg
    .append('g')
    .attr('transform', `translate(0,${chart_height})`);

  const brw = binfo_width * 0.7;
  const brh = binfo_height * 0.75;
  const brx = (full_width - brw) / 2;
  const bry = (binfo_height - brh) / 2;

  binfo
    .append('rect')
    .attr('x', brx)
    .attr('y', bry)
    .attr('rx', 30)
    .attr('width', brw)
    .attr('height', brh)
    .attr('fill', 'none')
    // .attr('stroke', 'black')
    .attr('stroke-width', 2);

  console.log(data);
  const top_contributors = Object.entries(data.contributors)
    .sort(([, a], [, b]) => b.contributions - a.contributions)
    .slice(0, 5);

  binfo
    .append('text')
    .attr('class', 'info-title')
    .attr('x', brx + textmargin.x)
    .attr('y', bry + textmargin.y)
    .text('Top Contributors');

  const contributors = binfo
    .append('g')
    .attr('transform', `translate(${brx + textmargin.x}, ${bry})`);

  contributors
    .selectAll('text')
    .data(top_contributors)
    .enter()
    .append('text')
    .attr('y', (_, i) => textmargin.y * (i + 2))
    .text(
      ([name, attr]) =>
        `${name} - Contributions: ${attr.contributions} - URL: ${attr.url}`
    );

  const sinfo = svg
    .append('g')
    .attr('id', 'sinfo')
    .attr('transform', `translate(${chart_width}, 0)`);

  const srw = sinfo_width * 0.9;
  const srh = sinfo_height * 0.95;
  const srx = (full_width - chart_width - srw) / 2;
  const sry = (sinfo_height - srh) / 2;

  sinfo
    .append('rect')
    .attr('x', srx)
    .attr('y', sry)
    .attr('rx', 30)
    .attr('width', srw)
    .attr('height', srh)
    .attr('fill', 'none')
    // .attr('stroke', 'black')
    .attr('stroke-width', 2);

  sinfo
    .append('text')
    .attr('class', 'info-title')
    .attr('x', srx + textmargin.x)
    .attr('y', sry + textmargin.y)
    .text('Information');

  sinfo
    .append('g')
    .attr('class', 'items')
    .attr(
      'transform',
      `translate(${srx + textmargin.x}, ${sry + textmargin.y})`
    );

  function mouseover(_, d) {
    var info = [
      d.clone_url,
      `Language: ${d.language}`,
      `Last update: ${d.last_update}`,
      `Days Since update: ${d.days_since_updated}`,
      `Total lines: ${d.lines}`,
      `Effective_lines: ${d.effective_lines}`,
    ];

    if (d.definitions !== undefined) {
      // console.log(d.definitions);
      const def = d.definitions;
      // classes
      if (def.classes.length > 0) {
        info.push('Classes');
        def.classes.forEach((e) => {
          info.push(`- ${e.name}: ${e.line}`);
        });
      }
      // functions
      if (def.functions.length > 0) {
        info.push('Functions');
        def.functions.forEach((e) => {
          info.push(`- ${e.name}: ${e.line}`);
        });
      }
      // imports
      // if (def.imports.length > 0) {
      //   info.push('Imports');
      //   def.imports.forEach((e) => {
      //     console.log(e);
      //     info.push(`- ${e.namespace}`);
      //   });
      // }
    }

    const items = d3
      .select('#sinfo')
      .select('.items')
      .selectAll('.item')
      .data(info);

    items.join(
      (enter) => {
        enter
          .append('text')
          .attr('class', 'item')
          .attr('y', (_, i) => textmargin.y * (i + 1))
          .text((d) => d);
      },
      (update) => {
        update.text((d) => d);
      },
      (exit) => exit.remove()
    );

    d3.select('#chart').selectAll('rect').attr('opacity', 0.7);
    d3.select(this).attr('opacity', 1);
  }

  function mouseout(_, d) {
    d3.select('#sinfo').select('.items').selectAll('.item').remove();
    d3.select('#chart').selectAll('rect').attr('opacity', 1);
  }
}

d3.json('colors.json').then((data) => (lang_colors = data));

d3.json('data.json').then((data) => {
  // console.log(data);
  render(data);
});
