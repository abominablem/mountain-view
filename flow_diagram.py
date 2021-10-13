# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 20:02:09 2021

@author: marcu
"""

from mh_logging import log
from PIL import Image, ImageDraw, ImageFont
from mountain_view_alteryx import Workflow
from datetime import datetime


class FlowDiagram:
    scale = 2
    node_height = 50*scale
    node_width = node_height
    grid_spacing = 75*scale
    node_thickness = 6*scale
    connection_thickness = 3*scale
    container_thickness = 2*scale
    container_padding = 10
    #offsets from the centre of the 
    connection_offsets = {1: [int(node_width/2)],
                          2: [int(node_height/3), 2*int(node_height/3)],
                          3: [int(node_height/4), int(node_height/2), 3*int(node_height/4)]
                          }
    #first is the key for connection_offsets above
    #second is the index of the Y offset in the array
    connection_type_offset = {"input": {"Target": (0, 2),
                                        "Source": (1, 2),
                                        "Left": (0, 2),
                                        "Right": (1, 2),
                                        "ContainerInput": (0, 1)
                                        },
                              "output": {"Left": (0, 3),
                                         "Join": (1, 3),
                                         "Right": (2, 3),
                                         "True": (0, 2),
                                         "False": (1, 2),
                                         "Unique": (0, 2),
                                         "Duplicate": (1, 2),
                                         "ContainerOutput": (0, 1)
                                         }
                              }
    background = 'white'
    border = node_width
    font = ImageFont.truetype("arial.ttf", 18)
    def __init__(self, workflow, trace = None):
        log.log_trace(self, "__init__", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".__init__"}
        """
        Initialise a new flow diagram canvas to add nodes and connections to.
        """
        self.workflow = workflow
        for n in self.workflow.nodes:
            n.x = n.x*self.scale
            n.y = n.y*self.scale
            
        for c in self.workflow.containers:
            c.x = c.x*self.scale
            c.y = c.y*self.scale
            c.width = c.width*self.scale
            c.height = c.height*self.scale
                
        self.x_offset = -1*min(workflow.nodes.attr('x')) + self.border
        self.y_offset = -1*min(workflow.nodes.attr('y')) + self.border
        
        for n in self.workflow.nodes:
            n.x += self.x_offset
            n.y += self.y_offset     
        for c in self.workflow.containers:
            c.x += self.x_offset
            c.y += self.y_offset
                
        x_max = max(workflow.nodes.attr('x')) + self.node_width + self.border
        
        y_max = max(workflow.nodes.attr('y')) + self.node_height + self.border
        
        self.canvas = Image.new('RGB', (x_max, y_max), color = 'white')
        self.draw = ImageDraw.Draw(self.canvas)
        
        for c in self.workflow.containers:
            self.draw_container(c, trace = inf_trace)
     
        for n in self.workflow.nodes:
            if n.is_container:
                pass
            else:
                self.draw_node(n, trace = inf_trace)
            
        for c in self.workflow.connections:
            if c.wireless:
                pass
            else:
                self.draw_connector(c, trace = inf_trace)
        
        
    def _node_coords(self, n, trace = None):
        log.log_trace(self, "draw_node", trace)
        """
        Get the coordinates for a given node object
        """
        x1 = n.x
        y1 = n.y
        x2 = x1 + self.node_width
        y2 = y1 + self.node_height
        return (x1, y1, x2, y2)
    
    def _container_coords(self, c, trace = None):
        log.log_trace(self, "draw_node", trace)
        """
        Get the coordinates for a given node object
        """
        x1 = c.x
        y1 = c.y
        x2 = x1 + c.width + self.container_padding
        y2 = y1 + c.height + self.container_padding
        return (x1, y1, x2, y2)
        
    def draw_node(self, n, trace = None):
        log.log_trace(self, "draw_node", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".draw_node"}
        """
        Add a node to the canvas from a Node object
        """
        x1, y1, x2, y2 = self._node_coords(n, inf_trace)
        self._square([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])
        self._text((x1, y1 - 2*self.node_thickness), n.type)
        self._text((x1 + self.node_thickness, y1 + 2*self.node_thickness), n.id)
        
    def draw_container(self, c, trace = None):
        log.log_trace(self, "draw_container", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".draw_container"}
        """
        Add a container to the canvas from a Container object
        """
        x1, y1, x2, y2 = self._container_coords(c, inf_trace)
        self._box(vertices = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)],
                  outline = c.border_colour,
                  fill = c.fill_colour,
                  width = self.container_thickness,
                  trace = inf_trace)
        self._text((x1 + self.container_thickness, 
                    y1 + self.container_thickness), 
                   c.id + " " + c.caption)
        
    def _square(self, vertices, colour = 'black', width = None, trace = None):
        log.log_trace(self, "_square", trace)
        """
        Draw a polygon with rounded edges between the given vertices
        """
        width = self.node_thickness if width is None else width
        vertices += vertices
        self.draw.line(vertices, fill = colour, 
                       width = width, joint = "curve")
        
    def _box(self, vertices, outline, fill, width = None, trace = None):
        log.log_trace(self, "_square", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + "._box"}
        """
        Draw a filled polygon with rounded edges between the given vertices
        """
        width = self.node_thickness if width is None else width
        vertices += vertices
        
        self.draw.rectangle([vertices[0], vertices[2]], 
                            fill, outline, width)
        self._square(vertices, colour = outline, 
                     width = width, trace = inf_trace)
        
    def _text(self, xy, text, colour = 'black', trace = None):
        log.log_trace(self, "_square", trace)
        """
        Add text to the canvas at the given coordinates
        """
        self.draw.text(xy, text, colour, font = self.font)
        
    def draw_connector(self, c, split = True, colour = 'black', 
                       width = None, trace = None):
        log.log_trace(self, "draw_connector", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + ".draw_connector"}
        """
        Add a connector to the canvas from a Connector object
        """
        width = self.connection_thickness if width is None else width
        coords = self._connection_coords(c, trace = inf_trace)
        if split:
            x1, y1, x2, y2 = (coords[0][0], coords[0][1], 
                              coords[1][0], coords[1][1])
            
            split_coords = ((x1, y1), (int((x1+x2)/2), y1), 
                            (int((x1+x2)/2), y2), (x2, y2))
            
            self.draw.line(split_coords, fill = colour, 
                           width = width, joint="curve")
        else:
            self.draw.line(coords, fill = colour, width = width)
        
    def _connection_coords(self, c, trace = None):
        log.log_trace(self, "draw_connector", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + "._connection_coords"}
        """
        Get the coordinates of the start and end of a connection
        """
        start_node = self.workflow.nodes.get_node(c.origin.id)
        end_node = self.workflow.nodes.get_node(c.destination.id)
        
        coords = [[start_node.x, start_node.y],
                  [end_node.x, end_node.y]]
        if start_node.is_container:
            coords_offset = [[150, 0], [0, 0]]
        else:
            coords_offset = [[self.node_width, 0], [0, 0]]
        
        """ offset the connection start/end vertically based on the type of 
        connection """
        off = self.connection_type_offset["output"].get(c.origin.type, (0, 1))
        coords_offset[0][1] = self.connection_offsets[off[1]][off[0]]
        
        off = self.connection_type_offset["input"].get(c.destination.type, (0, 1))
        coords_offset[1][1] = self.connection_offsets[off[1]][off[0]]
        
        for i in [0, 1]:
            coords[i] = self._offset(coords[i], coords_offset[i], inf_trace)
            
        return tuple(coords)
        
    def _offset(self, xy, offset_xy, trace = None):
        log.log_trace(self, "draw_connector", trace)
        return(tuple(xy[i] + offset_xy[i] for i in range(len(xy))))
    
    def show(self, trace = None):
        log.log_trace(self, "show", trace)
        self.canvas.show()
        
    def save(self, trace = None):
        log.log_trace(self, "save", trace)
        str_dt = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        filename = "%s %s.png" % (self.workflow.name, str_dt)
        self.canvas.save(".\Images\%s" % filename)
        
if __name__ == "__main__":
    workflow = Workflow("..\\Workflows\\ar-sc.txt",
                        trace = {"source": "initialise class", 
                                 "parent": __name__})
    
    meta_workflow = workflow.build_meta_workflow("Check")
    
    flow = FlowDiagram(meta_workflow)
    flow.show()
    flow.save()