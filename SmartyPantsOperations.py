from datetime import date, datetime
from bokeh.embed import components
from bokeh.models import TabPanel, Tabs, Span, HoverTool, ColumnDataSource, Range1d, PanTool, SaveTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.plotting import figure
import pandas as pd
from bokeh.palettes import Light, Category10
from math import pi
from bokeh.transform import cumsum
from bokeh.layouts import gridplot

class Operations:
    def calculateAge(dob):
        x = datetime.strptime(dob, '%Y-%m-%d')
        today = date.today()
        one_or_zero = ((today.month, today.day) < (x.month, x.day))
        year_difference = today.year - x.year
        y = 1 if one_or_zero else 0
        curr_age = year_difference - y
        return curr_age
    
    def generateGraph(x, y):
        source = ColumnDataSource(data=dict(x=x, y=y))
        hover = HoverTool(tooltips=[('Score', "@y")])
        
        upper = Span(location=75, dimension='width', line_color='green', line_width=2, line_dash='dashed', name="Pass", hover_line_cap="round")
        
        
        bar_plot = figure(title="Bar Plot", x_range=x, y_range=Range1d(0,101), width=800, height=500, toolbar_location="below", 
                          tools="pan,wheel_zoom,box_zoom,reset")
        bar_plot.vbar(x='x', top='y', width=0.5, source=source, line_color="navy", fill_color="orange", fill_alpha=0.5)
        bar_plot.add_layout(upper)

        bar_plot.xaxis.axis_label = "Content"
        bar_plot.xaxis.axis_line_width = 3
        
        bar_plot.yaxis.axis_label = "Score"
        bar_plot.yaxis.major_label_text_color = "orange"
        
        bar_plot.toolbar.logo = None
        bar_plot.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        
        circle_plot = figure(title="Circle Plot", x_range=x, y_range=Range1d(0,101), width=800, height=500, toolbar_location="below", 
                             tools="pan,wheel_zoom,box_zoom,reset")
        circle_plot.circle(x, y, size=25, color="firebrick", alpha=0.5)
        circle_plot.add_layout(upper)
        circle_plot.add_tools(hover)
        
        circle_plot.xaxis.axis_label = "Content"
        circle_plot.xaxis.axis_line_width = 3
    
        circle_plot.yaxis.axis_label = "Score"
        circle_plot.yaxis.major_label_text_color = "orange"

        circle_plot.toolbar.logo = None
        circle_plot.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        
        tab1 = TabPanel(child=bar_plot, title="Bar Graph Analysis")
        tab2 = TabPanel(child=circle_plot, title="Dot Graph Analysis")
        tabs = Tabs(tabs=[tab1, tab2])

        script, div = components(tabs)
        return script, div
    
    def generateTimeGraph(time):       
        data = {"Activity": ["Learning", "Playing", "Reading"], "Time": time}
        data = pd.DataFrame(data)
        data['angle'] = data['Time'] / data['Time'].sum() * 2 * pi
        data['colors'] = Light[len(data)]
        hover = HoverTool(tooltips=[("Activity", "@Activity"),('Time spent', "@Time mins")])
        p = figure(title="Time Spent on Activities", height=400, x_range=(-0.5, 0.75), width=500)
        p.toolbar.logo = None
        p.xaxis.major_label_text_font_size = '0pt'
        p.xaxis.axis_label = None
        p.xgrid.grid_line_color = None
        p.xaxis.axis_line_width = 0
        p.xaxis.major_tick_line_color = None
        p.xaxis.minor_tick_line_color = None
        
        p.yaxis.major_label_text_font_size = '0pt'
        p.yaxis.axis_label = None
        p.ygrid.grid_line_color = None
        p.yaxis.axis_line_width = 0
        p.yaxis.major_tick_line_color = None
        p.yaxis.minor_tick_line_color = None
        
        p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white",  legend_field='Activity', source=data, fill_color='colors')
        p.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        
        hover = HoverTool(tooltips=[("Activity", "@x"),('Time spent', "@top mins")])
        barGraph = figure(x_range=data['Activity'], height=400, width=500)
        barGraph.vbar(x=data['Activity'], top=data['Time'], width=0.5, color=Light[3])
        barGraph.toolbar.logo = None
        barGraph.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        barGraph.xaxis.axis_label = "Activity"
        barGraph.xaxis.axis_line_width = 3 
        barGraph.yaxis.axis_label = "Time"
        barGraph.yaxis.major_label_text_color = "orange"
        
        grid = gridplot([[p, barGraph]])
        
        return components(grid)
    
    def generateProfileGraph(scores):
        x1 = ["Alphabets-1", "Alphabets-2", "Alphabets-3", "Alphabets-4"]
        y1 = scores[0:4]
        
        x2 = ["Herbivores Animals", "Carnivores Animals", "Omnivores Animals"]
        y2 = scores[4:7]
        
        x3 = ["Fishes", "Birds", "Prehistoric Animals"]
        y3 = scores[7:10]
        
        x4 = ["Rhyme-1", "Rhyme-2", "Rhyme-3", "Rhyme-4", "Rhyme-5"]
        y4 = scores[10:15]
        
        color = Category10[10]
        hover = HoverTool(tooltips=[("Category", "@x"), ('Score', "@top")])
        
        #plot1 = generate_bar_plot(x1, y1, "Alphabets")
        plot1 = figure(x_range=x1, title="Alphabets", height=400, width=500)
        plot1.vbar(x=x1, top=y1, width=0.5, color=color[0])
        plot1.toolbar.logo = None
        plot1.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        plot1.xaxis.axis_label = "Content"
        plot1.xaxis.axis_line_width = 3 
        plot1.yaxis.axis_label = "Score"
        plot1.yaxis.major_label_text_color = "orange"
        
        #plot2 = generate_bar_plot(x2, y2, "Animal Types")
        plot2 = figure(x_range=x2, title="Animals-1", height=400, width=500)
        plot2.vbar(x=x2, top=y2, width=0.5, color=color[1])
        plot2.toolbar.logo = None
        plot2.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        plot2.xaxis.axis_label = "Content"
        plot2.xaxis.axis_line_width = 3 
        plot2.yaxis.axis_label = "Score"
        plot2.yaxis.major_label_text_color = "orange"
        
        #plot3 = generate_bar_plot(x3, y3, "Animal Categories")
        plot3 = figure(x_range=x3, title="Animals-2", height=400, width=500)
        plot3.vbar(x=x3, top=y3, width=0.5, color=color[2])
        plot3.toolbar.logo = None
        plot3.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        plot3.xaxis.axis_label = "Content"
        plot3.xaxis.axis_line_width = 3 
        plot3.yaxis.axis_label = "Score"
        plot3.yaxis.major_label_text_color = "orange"
        
        #plot4 = generate_bar_plot(x4, y4, "Rhymes")
        plot4 = figure(x_range=x4, title="Rhymes", height=400, width=500)
        plot4.vbar(x=x4, top=y4, width=0.5, color=color[3])
        plot4.toolbar.logo = None
        plot4.tools = [SaveTool(), PanTool(), BoxZoomTool(), WheelZoomTool(), hover, ResetTool()]
        plot4.xaxis.axis_label = "Content"
        plot4.xaxis.axis_line_width = 3 
        plot1.yaxis.axis_label = "Score"
        plot4.yaxis.major_label_text_color = "orange"
        
        # Arrange the plots in a grid
        grid = gridplot([[plot1, plot2], [plot3, plot4]])

        # Convert the grid of plots to Bokeh script and div components
        script, div = components(grid)
        return script, div