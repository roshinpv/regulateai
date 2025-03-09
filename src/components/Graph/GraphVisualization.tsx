import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Database } from 'lucide-react';
import { GraphData } from '../../types';

interface GraphVisualizationProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (nodeId: string, nodeType: string) => void;
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    setIsLoading(true);

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .append("g");

    // Add zoom functionality
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        svg.attr("transform", event.transform);
      });

    d3.select(svgRef.current).call(zoom);

    // Create a force simulation
    const simulation = d3.forceSimulation(data.nodes as d3.SimulationNodeDatum[])
      .force("link", d3.forceLink(data.links)
        .id((d: any) => d.id)
        .distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(50));

    // Create links
    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("class", "link");

    // Create link labels
    const linkLabels = svg.append("g")
      .selectAll("text")
      .data(data.links)
      .enter()
      .append("text")
      .attr("class", "link-label")
      .attr("font-size", "10px")
      .attr("text-anchor", "middle")
      .attr("dy", "-5")
      .text((d) => d.label);

    // Create nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("class", (d) => `node node-${d.type}`)
      .attr("r", 15)
      .on("click", (event, d: any) => {
        if (onNodeClick) {
          onNodeClick(d.id, d.type);
        }
      })
      .call(d3.drag<SVGCircleElement, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Create node labels
    const nodeLabels = svg.append("g")
      .selectAll("text")
      .data(data.nodes)
      .enter()
      .append("text")
      .attr("font-size", "12px")
      .attr("text-anchor", "middle")
      .attr("dy", "30")
      .text((d) => d.label);

    // Update positions on each tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      linkLabels
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);

      nodeLabels
        .attr("x", (d: any) => d.x)
        .attr("y", (d: any) => d.y);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    setIsLoading(false);

    return () => {
      simulation.stop();
    };
  }, [data, width, height, onNodeClick]);

  if (!data.nodes.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Database size={48} className="text-neutral-light mb-4" />
        <h3 className="text-lg font-medium text-neutral mb-2">No Data Available</h3>
        <p className="text-neutral-light text-center max-w-md">
          There are no regulations, agencies, or banks to visualize.
        </p>
      </div>
    );
  }
  
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Regulatory Knowledge Graph</h2>
        <div className="flex space-x-2">
          <button className="btn btn-outline text-sm">Filter</button>
          <button className="btn btn-outline text-sm">Expand All</button>
          <button className="btn btn-outline text-sm">Reset</button>
        </div>
      </div>
      <div className="border border-neutral-lighter rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center" style={{ height: '500px' }}>
            <p className="text-neutral-light">Loading graph...</p>
          </div>
        ) : (
          <svg ref={svgRef} className="w-full" style={{ minHeight: '500px' }}></svg>
        )}
      </div>
    </div>
  );
};

export default GraphVisualization;