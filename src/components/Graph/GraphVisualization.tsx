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
    
    // Create SVG container
    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);
    
    // Create container group for zoom
    const g = svg.append("g");
    
    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });
    
    svg.call(zoom);
    
    // Create arrow marker for directed edges
    svg.append("defs").selectAll("marker")
      .data(["end"])
      .enter().append("marker")
      .attr("id", String)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#999");
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links)
        .id((d: any) => d.id)
        .distance(100))
      .force("charge", d3.forceManyBody()
        .strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide()
        .radius(50));
    
    // Create links
    const links = g.append("g")
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1)
      .attr("marker-end", "url(#end)");
    
    // Create link labels
    const linkLabels = g.append("g")
      .selectAll("text")
      .data(data.links)
      .enter()
      .append("text")
      .attr("class", "link-label")
      .attr("font-size", "10px")
      .attr("text-anchor", "middle")
      .attr("dy", "-5")
      .text((d) => d.label);
    
    // Create node groups
    const nodes = g.append("g")
      .selectAll("g")
      .data(data.nodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .call(d3.drag<any, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
    
    // Add circles to nodes
    nodes.append("circle")
      .attr("r", 15)
      .attr("fill", (d) => getNodeColor(d.type))
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);
    
    // Add node labels
    nodes.append("text")
      .attr("dy", 25)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .text((d) => d.label);
    
    // Add click handler to nodes
    nodes.on("click", (event, d: any) => {
      if (onNodeClick) {
        onNodeClick(d.id, d.type);
      }
    });
    
    // Update positions on each tick
    simulation.on("tick", () => {
      links
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      
      linkLabels
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);
      
      nodes
        .attr("transform", (d: any) => `translate(${d.x},${d.y})`);
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
    
    // Get node color based on type
    function getNodeColor(type: string): string {
      switch (type) {
        case 'regulation':
          return '#4CAF50';
        case 'agency':
          return '#FF9800';
        case 'bank':
          return '#2196F3';
        default:
          return '#9E9E9E';
      }
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