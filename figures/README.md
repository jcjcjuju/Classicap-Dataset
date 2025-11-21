# Dataset Visualizations

This directory contains comprehensive statistical visualizations of the Classicap dataset.

## Overview of Plots

### 1. `comprehensive_summary.png` - Complete Overview
A single-page dashboard showing all key statistics:
- Duration distribution histogram
- Caption density (words/second) distribution
- Word count distribution
- Caption density vs duration scatter plot
- Word count vs duration correlation
- Composer distribution bar chart
- Summary statistics table

**Best for**: Quick overview and presentations

---

### 2. `duration_distribution.png` - Audio Segment Length Analysis
Simple histogram showing segment duration distribution with statistics overlay.

**Key Insights**:
- Average segment: 125.8 seconds (~2 minutes)
- Median: 104.8 seconds
- Range: 5.9s to 742.9s (over 12 minutes)
- Most segments fall between 1-3 minutes

---

### 3. `caption_density_distribution.png` - Description/Duration Ratio
Histogram of the **description/duration ratio** (our custom metric: words per second).

**Key Insights**:
- Average: **1.39 words/second**
- Median: **1.15 words/second**
- Range: 0.16 - 10.32 words/sec
- This metric reveals how caption density adapts to musical complexity
- Lower density for simple passages, higher for complex analytical sections

**Why this matters**:
- Ensures captions are neither too sparse (uninformative) nor too dense (overwhelming)
- Shows dataset diversity in annotation granularity
- Useful for training audio captioning models with varied detail levels

---

### 4. `word_count_distribution.png` - Caption Length Analysis
**Why this matters**:
- Balances informativeness vs verbosity
- Adapts to different musical contexts (simple melodies vs complex analysis)
- Ensures captions are neither too sparse nor overwhelming

---

### 4. `composer_distribution.png` - Repertoire Diversity
Bar chart showing number of segments per composer with percentages.

**Key Insights**:
- Beethoven: 51.2% (281 segments)
- Mozart: 25.0% (137 segments)
- Bach: 17.5% (96 segments - Well-Tempered Clavier)
- Chopin: 4.4% (24 segments)
- Schubert: 2.0% (11 segments)

---

### 5. `pianist_distribution.png` - Performer Representation
Bar chart showing top 10 pianists by number of segments.

**Key Insights**:
- 12 renowned pianists total
- Daniel Barenboim: 70.1% (385 segments)
- András Schiff: 6.9% (38 segments)
- Ivan Moravec: 5.3% (29 segments)
- Other notable performers: Evgeny Kissin, Seong-Jin Cho, Sviatoslav Richter, Krystian Zimerman

**Why this matters**:
- Demonstrates professional-quality performances
- Allows style-specific analysis (e.g., comparing different interpretations)

---

### 6. `avg_loudness_db_distribution.png` - Audio Loudness Consistency
Histogram showing average RMS loudness distribution across all segments.

**Key Insights**:
- Average: -28.9 dB (±4.6 dB)
- Consistent recording levels across dataset
- Minimal variation ensures reliable audio processing

---

### 7. `snr_estimate_db_distribution.png` - Signal-to-Noise Ratio
Histogram showing estimated SNR for all audio segments.

**Key Insights**:
- Average: 40.7 dB (±8.2 dB)
- High-quality recordings with minimal background noise
- Suitable for machine learning applications

---

### 8. `dynamic_range_db_distribution.png` - Dynamic Range Analysis
Histogram showing dynamic range (peak - average loudness) distribution.

**Key Insights**:
- Average: 21.5 dB (±2.9 dB)
- Preserves natural piano dynamics
- Balances loudness normalization with musical expressiveness

---

## Technical Details

**Plot Generation**:
- Library: matplotlib + seaborn
- Resolution: 300 DPI
- Format: PNG with tight bounding boxes
- Color scheme: Professional color palettes from seaborn

**Statistics Calculation**:
- Duration: Calculated from audio file lengths
- Caption metrics: Parsed from .caption.txt files
- Audio quality: Analyzed using librosa (RMS loudness, SNR estimation, dynamic range)
- Pianist info: Extracted from metadata CSV

**File Sizes**:
- Individual plots: ~120-130 KB each
- Comprehensive summary: ~710 KB
- Total: ~1.5 MB for all visualizations

---

## Understanding the Description/Duration Ratio

The **description/duration ratio** (words per second) is a custom metric we created to quantify caption density:

- **Low ratio (< 0.5 words/sec)**: Sparse captions, minimal description
- **Medium ratio (0.5-1.5 words/sec)**: Balanced captions, moderate detail
- **High ratio (> 1.5 words/sec)**: Dense captions, detailed analysis

### Why it's useful:
1. **Dataset Quality**: Ensures consistent annotation density
2. **Training Models**: Helps select appropriate samples for different tasks
3. **Diversity Metric**: Shows the dataset covers varied complexity levels
4. **Comparison**: Can compare with other audio captioning datasets

Our dataset's mean of **1.39 words/sec** indicates well-balanced captions that provide substantial musical information without being overwhelming.

---

## Interpretation Guide

### For ML Researchers:
- **Duration distribution**: Shows input sequence length variety for models
- **Caption density**: Indicates annotation granularity consistency
- **Audio quality metrics**: Validates dataset suitability for acoustic modeling
- **Pianist distribution**: Enables performer-specific analysis or style transfer

### For Music Information Retrieval:
- **Repertoire diversity**: Covers major piano literature periods
- **Dynamic range**: Preserves authentic performance dynamics
- **SNR quality**: Ensures clean spectral features extraction

### For Dataset Users:
- **Comprehensive summary**: Quick overview of what the dataset offers
- **Individual plots**: Deep dive into specific aspects of interest
- **Statistics overlay**: Exact numerical values for validation

---

**Generated**: January 2025  
**Dataset Version**: 1.0

