import os
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib

# Set font to Arial to ensure all text is in English
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 16

# Define tools and instances
TOOLS = ['AFL', 'AFLFast', 'MAflood']
INSTANCES = ['m', 's1', 's2', 's3']
BASE_PATH = 'f:\\浙江警察学院\\MAflood-Data\\experiment\\LAVA-M'

# Define colors and line styles
COLORS = {'AFL': '#FF6B6B', 'AFLFast': '#4ECDC4', 'MAflood': '#45B7D1'}
LINE_STYLES = {'AFL': 'solid', 'AFLFast': 'dashed', 'MAflood': 'dotted'}


def read_fuzzer_stats(tool, instance):
    """Read fuzzer_stats file, extract execution count and unique crashes"""
    stats_path = os.path.join(BASE_PATH, tool, '4', 'fuzz_out', instance, 'fuzzer_stats')
    if not os.path.exists(stats_path):
        return {'execs_done': 0, 'unique_crashes': 0}
    
    stats = {}
    with open(stats_path, 'r') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == 'execs_done':
                    stats['execs_done'] = int(value)
                elif key == 'unique_crashes':
                    stats['unique_crashes'] = int(value)
    
    return stats


def read_plot_data(tool, instance):
    """Read plot_data file, extract coverage data, sample at 1-minute intervals, 24-hour limit"""
    plot_path = os.path.join(BASE_PATH, tool, '4', 'fuzz_out', instance, 'plot_data')
    if not os.path.exists(plot_path):
        return []
    
    data = []
    with open(plot_path, 'r') as f:
        header = next(f)  # Skip header
        for line in f:
            parts = line.strip().split(', ')
            if len(parts) >= 7:
                unix_time = int(parts[0])
                map_size = parts[6]  # Coverage data
                # Convert coverage to percentage
                coverage = float(map_size.rstrip('%'))
                data.append({'time': unix_time, 'coverage': coverage})
    
    # Sort by time
    data.sort(key=lambda x: x['time'])
    
    # Sample processing: 1 minute per point, 24-hour limit
    if not data:
        return []
    
    start_time = data[0]['time']
    end_time = min(start_time + 24 * 3600, data[-1]['time'])
    
    sampled_data = []
    current_time = start_time
    
    while current_time <= end_time:
        # Find current time point or nearest time point
        closest_data = min(data, key=lambda x: abs(x['time'] - current_time))
        # Calculate hours
        hours = (current_time - start_time) / 3600
        sampled_data.append({'hour': hours, 'coverage': closest_data['coverage']})
        current_time += 60  # Increase by 1 minute
    
    return sampled_data


def collect_all_data():
    """Collect data for all tools and instances"""
    all_data = {}
    
    for instance in INSTANCES:
        instance_data = {}
        for tool in TOOLS:
            stats = read_fuzzer_stats(tool, instance)
            coverage_data = read_plot_data(tool, instance)
            instance_data[tool] = {
                'execs_done': stats['execs_done'],
                'unique_crashes': stats['unique_crashes'],
                'coverage_data': coverage_data
            }
        all_data[instance] = instance_data
    
    # Calculate combined data (average of all instances)
    combined_data = {}
    for tool in TOOLS:
        execs_done_list = []
        unique_crashes_list = []
        coverage_data_list = []
        
        for instance in INSTANCES:
            data = all_data[instance][tool]
            execs_done_list.append(data['execs_done'])
            unique_crashes_list.append(data['unique_crashes'])
            coverage_data_list.append(data['coverage_data'])
        
        # Calculate sum for execs_done and unique_crashes, average for coverage
        combined_data[tool] = {
            'execs_done': int(np.sum(execs_done_list)),
            'unique_crashes': int(np.sum(unique_crashes_list)),
            'coverage_data': average_coverage_data(coverage_data_list)
        }
    
    all_data['combined'] = combined_data
    return all_data


def average_coverage_data(coverage_data_list):
    """Calculate average coverage data for multiple instances"""
    if not coverage_data_list:
        return []
    
    # Find the longest dataset
    max_length = max(len(data) for data in coverage_data_list)
    
    # Align and calculate average
    averaged_data = []
    for i in range(max_length):
        hour = 0
        coverage_sum = 0
        count = 0
        
        for data in coverage_data_list:
            if i < len(data):
                hour = data[i]['hour']
                coverage_sum += data[i]['coverage']
                count += 1
        
        if count > 0:
            averaged_data.append({'hour': hour, 'coverage': coverage_sum / count})
    
    return averaged_data


def save_data_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def generate_bar_chart(data, instance):
    """Generate bar chart"""
    fig, ax1 = plt.subplots(figsize=(12, 8))  # 1.5:1 ratio
    
    # Set colors and labels
    tools = TOOLS
    metrics = ['execs_done', 'unique_crashes']
    
    # Prepare data
    execs_data = []
    crashes_data = []
    labels = []
    legend_labels = []  # Legend labels
    
    for tool in tools:
        execs_data.append(data[tool]['execs_done'])
        crashes_data.append(data[tool]['unique_crashes'])
        labels.append(f"{tool}-exec")
        labels.append(f"{tool}-crash")
        legend_labels.append(f"{tool}-Execution Count")
        legend_labels.append(f"{tool}-Unique Crashes")
    
    # Set X-axis positions
    x = np.arange(len(labels))
    width = 0.35  # Narrow width
    
    # Create second Y-axis (for displaying Unique Crashes scale)
    ax2 = ax1.twinx()
    
    # Draw bar chart - draw each bar individually to create independent legend entries
    # Execution Count uses solid color, Unique Crashes uses grid fill
    bars1 = []
    bars2 = []
    
    for i, tool in enumerate(tools):
        # Execution Count bars - solid color fill, drawn on ax1
        bar1 = ax1.bar(x[2*i], execs_data[i], width=width, color=COLORS[tool], 
                       label=legend_labels[2*i], alpha=1.0, edgecolor='black', linewidth=0.5)
        bars1.append(bar1)
        
        # Unique Crashes bars - grid fill (white background + grid), drawn on ax2
        bar2 = ax2.bar(x[2*i+1], crashes_data[i], width=width, color='white', 
                       edgecolor=COLORS[tool], hatch='///', linewidth=1.5,
                       label=legend_labels[2*i+1])
        bars2.append(bar2)
    
    # Set Y-axis labels
    ax1.set_ylabel('Execution Count', fontsize=16)
    ax2.set_ylabel('Unique Crashes', fontsize=16)
    
    # Set X-axis labels (not displayed)
    ax1.set_xticks(x)
    ax1.set_xticklabels([''] * len(labels))
    
    # Set Y-axis ranges
    ax1.set_ylim(0, max(execs_data) * 1.15)
    ax2.set_ylim(0, max(crashes_data) * 1.15 if max(crashes_data) > 0 else 1)
    
    # Add data labels
    for i, (exec_val, crash_val) in enumerate(zip(execs_data, crashes_data)):
        ax1.text(x[2*i], exec_val + 0.02 * max(execs_data), f'{exec_val:,}', ha='center', fontsize=14)
        ax2.text(x[2*i+1], crash_val + 0.02 * max(crashes_data), f'{crash_val}', ha='center', fontsize=14)
    
    # Add legend - display 6 test cases, placed in a row below X-axis
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    # Reorder legend, grouped by tool
    all_lines = []
    all_labels = []
    for i in range(len(tools)):
        all_lines.append(lines1[i])
        all_lines.append(lines2[i])
        all_labels.append(labels1[i])
        all_labels.append(labels2[i])
    
    legend = ax1.legend(all_lines, all_labels, loc='upper center', bbox_to_anchor=(0.5, -0.12), 
                        fontsize=10, ncol=3, frameon=True, 
                        fancybox=True, shadow=False, columnspacing=1.5)
    legend.set_zorder(100)  # Set legend z-order to highest
    
    # Set title
    if instance == 'combined':
        plt.title('Combined Fuzz Test Bar Chart', fontsize=20, pad=20)
    else:
        plt.title(f'Instance {instance} Fuzz Test Bar Chart', fontsize=20, pad=20)
    
    # Adjust layout to leave space for legend
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.22)
    
    # Save chart
    output_path = os.path.join(BASE_PATH, 'visualization', f'bar_chart_{instance}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_all_bar_charts(data):
    """Generate all bar charts"""
    chart_paths = {}
    for instance in INSTANCES + ['combined']:
        chart_path = generate_bar_chart(data[instance], instance)
        chart_paths[instance] = chart_path
        print(f"Bar chart generated: {chart_path}")
    return chart_paths


def generate_line_chart(data, instance):
    """Generate line chart"""
    fig, ax = plt.subplots(figsize=(12, 8))  # 1.5:1 ratio
    
    # Draw coverage curves for each tool
    for tool in TOOLS:
        coverage_data = data[tool]['coverage_data']
        if coverage_data:
            hours = [d['hour'] for d in coverage_data]
            coverage = [d['coverage'] for d in coverage_data]
            ax.plot(hours, coverage, label=tool, color=COLORS[tool], 
                    linestyle=LINE_STYLES[tool], linewidth=3)  # Thickest width
    
    # Set X-axis range and labels
    ax.set_xlim(0, 24)
    ax.set_xticks(np.arange(0, 25, 1))
    ax.set_xlabel('Time (Hour)', fontsize=16)
    
    # Set Y-axis label
    ax.set_ylabel('Code Coverage (%)', fontsize=16)
    
    # Add hourly data markers
    for tool in TOOLS:
        coverage_data = data[tool]['coverage_data']
        if coverage_data:
            # Take one point per hour
            hourly_data = []
            current_hour = 0
            for d in coverage_data:
                if d['hour'] >= current_hour:
                    hourly_data.append(d)
                    current_hour += 1
                    if current_hour > 24:
                        break
            
            # Add data markers
            for d in hourly_data:
                ax.text(d['hour'], d['coverage'] + 0.1, f'{d["coverage"]:.2f}', 
                        ha='center', va='bottom', fontsize=12, color=COLORS[tool])
    
    # Add legend
    ax.legend(loc='lower right', fontsize=14)
    
    # Set title
    if instance == 'combined':
        plt.title('Combined Fuzz Test Coverage Line Chart', fontsize=20)
    else:
        plt.title(f'Instance {instance} Fuzz Test Coverage Line Chart', fontsize=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save chart
    output_path = os.path.join(BASE_PATH, 'visualization', f'line_chart_{instance}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_all_line_charts(data):
    """Generate all line charts"""
    chart_paths = {}
    for instance in INSTANCES + ['combined']:
        chart_path = generate_line_chart(data[instance], instance)
        chart_paths[instance] = chart_path
        print(f"Line chart generated: {chart_path}")
    return chart_paths


def generate_combined_png(chart_paths, chart_type):
    """Generate combined PNG image"""
    from PIL import Image
    
    # Define layout parameters
    if chart_type == 'bar':
        title = 'LAVA-M Fuzzing Test Bar Charts'
    else:
        title = 'LAVA-M Fuzzing Test Coverage Line Charts'
    
    # Read all charts
    images = {}
    for instance in INSTANCES + ['combined']:
        img_path = os.path.join(BASE_PATH, 'visualization', f'{chart_type}_chart_{instance}.png')
        if os.path.exists(img_path):
            images[instance] = Image.open(img_path)
    
    # Calculate combined image size
    # Left side 4 small images, right side 1 large image (twice the size of small images)
    # Assume small image size is 1200x800
    small_width, small_height = 1200, 800
    large_width, large_height = small_width * 2, small_height * 2
    
    # Combined image size: left width + right width + margins
    total_width = small_width * 2 + large_width + 60
    total_height = large_height + 100  # Leave space at top for title
    
    # Create combined image
    combined_img = Image.new('RGB', (total_width, total_height), color='white')
    
    # Draw title
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(combined_img)
    font = ImageFont.truetype('arial.ttf', 32)
    text_width = draw.textlength(title, font=font)
    draw.text(((total_width - text_width) // 2, 30), title, font=font, fill='black')
    
    # Place left 4 small images (2x2 grid)
    positions = [
        (20, 100),          # m (1,1)
        (small_width + 30, 100),  # s1 (1,2)
        (20, small_height + 110),  # s2 (2,1)
        (small_width + 30, small_height + 110)  # s3 (2,2)
    ]
    
    for i, instance in enumerate(INSTANCES):
        if instance in images:
            img = images[instance]
            # Resize image to fit small image position
            img = img.resize((small_width, small_height))
            combined_img.paste(img, positions[i])
    
    # Place right large image
    if 'combined' in images:
        img = images['combined']
        # Resize image to fit large image position
        img = img.resize((large_width, large_height))
        combined_img.paste(img, (small_width * 2 + 40, 100))
    
    # Save combined image
    output_path = os.path.join(BASE_PATH, 'visualization', f'combined_{chart_type}_charts.png')
    combined_img.save(output_path, dpi=(300, 300))
    print(f"Combined PNG generated: {output_path}")
    
    return output_path


if __name__ == '__main__':
    # Create visualization directory if it doesn't exist
    os.makedirs(os.path.join(BASE_PATH, 'visualization'), exist_ok=True)
    
    # Collect data
    data = collect_all_data()
    
    # Save data to JSON file
    save_data_to_json(data, os.path.join(BASE_PATH, 'visualization', 'fuzzing_data.json'))
    print("Data collection completed, saved to visualization/fuzzing_data.json")
    
    # Generate bar charts
    bar_chart_paths = generate_all_bar_charts(data)
    
    # Generate line charts
    line_chart_paths = generate_all_line_charts(data)
    
    # Generate combined PNGs
    generate_combined_png(bar_chart_paths, 'bar')
    generate_combined_png(line_chart_paths, 'line')
