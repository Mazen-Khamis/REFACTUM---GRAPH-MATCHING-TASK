# Graph Matching and Visualization

## Overview

This project processes and analyzes graph-based data representing workpieces and their features. The main objectives are:

Load graph data from JSON files

Create graph objects using networkx

Check for subgraph matches between workpiece and feature graphs

Identify all possible subgraph matches

Generate visualizations and summaries

## Features

1. Load and Create Graphs

Reads workpiece_graph.json and feature_graph.json

Creates graphs using networkx.Graph()

Adds nodes and edges with attributes like type and angular_type

2. Subgraph Matching

Uses networkx.algorithms.isomorphism.GraphMatcher to detect subgraph isomorphisms

Identifies exact matches of the feature graph within the workpiece graph

Stores results in Results/Tables/subgraph_results.csv

3. Visualization

Saves static PNG visualizations of graphs with node labels

Generates interactive HTML graphs using pyvis

Highlights detected subgraph matches in a separate visualization

4. Results Summary

Generates a results_summary.html file containing:

Images of the graphs

Links to interactive graph visualizations

A table of identified subgraph matches

The summary opens automatically after execution

## How to Use

1. Install dependencies

pip install networkx matplotlib pandas pyvis

2. Run the script

python graph_search_task.py

3. View results

Check the Results/Graphs/ folder for PNG images

Open Results/HTML/results_summary.html for an interactive report

## Repository Structure

|-- Results/
|   |-- Graphs/         # Stores PNG images of graphs
|   |-- Tables/         # Stores CSV files of results
|   |-- HTML/           # Stores interactive HTML files
|-- workpiece_graph.json  # Workpiece graph data
|-- feature_graph.json    # Feature graph data
|-- graph_search_task.py  # Main script
|-- README.md            # This file



