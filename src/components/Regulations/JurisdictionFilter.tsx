import React, { useState, useEffect } from 'react';
import { Globe, ChevronDown, ChevronRight } from 'lucide-react';
import { Jurisdiction } from '../../types';

interface JurisdictionFilterProps {
  jurisdictions: Jurisdiction[];
  selectedJurisdiction: string | null;
  onJurisdictionChange: (jurisdictionId: string | null) => void;
}

interface JurisdictionNode extends Jurisdiction {
  children: JurisdictionNode[];
  expanded?: boolean;
}

const JurisdictionFilter: React.FC<JurisdictionFilterProps> = ({
  jurisdictions,
  selectedJurisdiction,
  onJurisdictionChange
}) => {
  const [jurisdictionTree, setJurisdictionTree] = useState<JurisdictionNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Build tree structure from flat jurisdictions list
    const buildTree = () => {
      const tree: JurisdictionNode[] = [];
      const map: Record<string, JurisdictionNode> = {};
      
      // First pass: create nodes with empty children arrays
      jurisdictions.forEach(jurisdiction => {
        map[jurisdiction.id] = {
          ...jurisdiction,
          children: [],
          expanded: expandedNodes[jurisdiction.id] || false
        };
      });
      
      // Second pass: build the tree
      jurisdictions.forEach(jurisdiction => {
        const node = map[jurisdiction.id];
        
        if (jurisdiction.parent_id) {
          // This is a child node
          if (map[jurisdiction.parent_id]) {
            map[jurisdiction.parent_id].children.push(node);
          }
        } else {
          // This is a root node
          tree.push(node);
        }
      });
      
      return tree;
    };
    
    setJurisdictionTree(buildTree());
  }, [jurisdictions, expandedNodes]);

  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodeId]: !prev[nodeId]
    }));
  };

  const renderJurisdictionNode = (node: JurisdictionNode, level: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes[node.id];
    const isSelected = selectedJurisdiction === node.id;
    
    return (
      <div key={node.id}>
        <div 
          className={`flex items-center py-2 px-2 rounded-md cursor-pointer ${
            isSelected ? 'bg-primary/10 text-primary' : 'hover:bg-neutral-lighter'
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => onJurisdictionChange(node.id)}
        >
          {hasChildren ? (
            <button 
              className="mr-1 p-1 rounded-full hover:bg-neutral-lighter"
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(node.id);
              }}
            >
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
          ) : (
            <span className="w-6"></span>
          )}
          <span className="flex-1">{node.name}</span>
          <span className="text-xs text-neutral-light">{node.type}</span>
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {node.children.map(child => renderJurisdictionNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="card mb-6">
      <div className="flex items-center mb-4">
        <div className="p-2 rounded-full bg-neutral-lighter mr-3">
          <Globe size={16} className="text-neutral" />
        </div>
        <h3 className="font-medium">Jurisdiction Filter</h3>
      </div>
      
      <div className="mb-2">
        <button 
          className={`w-full text-left px-4 py-2 rounded-md ${
            !selectedJurisdiction ? 'bg-primary text-white' : 'bg-neutral-lighter hover:bg-neutral-light hover:text-white'
          }`}
          onClick={() => onJurisdictionChange(null)}
        >
          All Jurisdictions
        </button>
      </div>
      
      <div className="max-h-64 overflow-y-auto">
        {jurisdictionTree.map(node => renderJurisdictionNode(node))}
      </div>
    </div>
  );
};

export default JurisdictionFilter;