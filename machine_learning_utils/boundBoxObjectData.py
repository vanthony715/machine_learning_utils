#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 11:40:05 2021
Description: Counts classes assuming file structure of Annotations and JPEGImages subfolders
@author: avasquez
"""
import os
import datetime
import xml.etree.ElementTree as ET
from tqdm import tqdm
import pandas as pd
import plotly.express as px

class GetBboxDict:
    
    '''
    Gets bounding box information for each object of an xml file. The bounding boxes 
    generated here are appended to a list, and that list is used as input to the Count Module
    '''
    
    def __init__(self, file, annotpath):
        self.file = file
        self.annotpath = annotpath
            
    ##gets chip coords from XML file
    def bbDict(self):
        tree = ET.parse(self.annotpath + self.file)
        root = tree.getroot()
        pre, _ =  os.path.splitext(self.file)
        
        self.bboxDict = {'clss':[], 'xmin':[], 'ymin':[], 'xmax':[], 'ymax':[], 
                       'file': []}
        
        for elem in root.iter('name'): 
            self.bboxDict['clss'].append(elem.text)
            self.bboxDict['file'].append(pre)
                
        for elem in root.iter('xmin'):
            self.bboxDict['xmin'].append(elem.text) 
            
        for elem in root.iter('ymin'): 
            self.bboxDict['ymin'].append(elem.text)
            
        for elem in root.iter('xmax'):
            self.bboxDict['xmax'].append(elem.text)
            
        for elem in root.iter('ymax'): 
            self.bboxDict['ymax'].append(elem.text)
            
        return self.bboxDict
        
class CountClasses:
    
    '''Module counts each class and associated bounding box coordinates present 
    in a list of bounding box dictionaries created by GetBboxDict.'''
    
    def __init__(self, bboxes):
        ##list of bounding boxes
        self.bboxes = bboxes
    
    def _calcArea(self, bb_dict, idx):
        
        '''Internal function that calculates bounding box area'''
        
        return (int(bb_dict['xmax'][idx]) - int(bb_dict['xmin'][idx])) * (int(bb_dict['ymax'][idx]) - int(bb_dict['ymin'][idx])) 
    
    def count(self):
        
        '''
        This function counts the each class and returns a count_df and the dataframe 
        that counts were derived from. The latter function is used to run statistics on
        the bounding box areas
        '''
        
        ##oject book keeping
        self.object_dict = {'clss': [], 'area':[]}
        
        ##iterate through bounding box list
        for _, bb_dict in tqdm(enumerate(self.bboxes), desc = 'counting classes', colour = 'blue'):
        
            for idx, clss in enumerate(bb_dict['clss']):
                
                ##get names and calculate areas
                self.object_dict['clss'].append(clss)
                self.object_dict['area'].append(self._calcArea(bb_dict, idx))
                
        ##get set
        classes = list(set(self.object_dict['clss']))
        dataframe = pd.DataFrame(self.object_dict)
        
        count_dict = {'clss': [], 'count': []}
        
        print('\nClass Count Summary: ')
        for clss in classes:
            print('Class: ', clss, 'Count:', 
                  dataframe[dataframe['clss'] == clss].clss.count())
            
            ##count book keeping -> used for PlotCount
            count_dict['clss'].append(clss)
            count_dict['count'].append(dataframe[dataframe['clss'] == clss].clss.count())
            
        ##convert to dataframe
        count_df = pd.DataFrame(count_dict)
            
        return count_df, dataframe
    
class DocumentProcess:
    
    '''simple plot library'''
    
    def __init__(self, plot_bars=True, show_plots=False, save_plots=True, write_counts = True, description='counts'):
        
        ##plot description -> plot name
        self.description = description
        
        ##boolean value
        self.plot_bars = plot_bars
        
        ##show plots
        self.show_plots = show_plots
        
        ##boolean to save plot
        self.save_plots = save_plots
        
        ##boolean to writes counts to text file
        self.write_counts = write_counts
        
    
    def plotCounts(self, dataframe, writepath='./'):
        
        '''plot barchart of class counts and saves data to text file'''
        
        time = str(datetime.datetime.now()).split('.', 1)[0]
        if self.plot_bars:
            fig = px.histogram(dataframe, x="clss", y="count", color="clss", 
                               hover_data=dataframe.columns)

            fig.update_layout(width = 800, 
                                  height =400, showlegend=True, title_x = 0.5,
                                  font=dict(size=16))
            if self.show_plots:
                fig.show()
                
            if self.save_plots:
                print('Saved Bar Plot to: ', writepath + self.description)
                fig.write_html(writepath + self.description + '_' + time + '.html')
                
            if self.write_counts:
                dataframe.to_csv(writepath + self.description + '_' + time + '.txt')
                print('Saved Summary to: ', writepath + self.description + '_' + time + '.txt')
                
    ##TODO think of a good way to visualize bounding box sizes.
    ##This might just to output size bins for each class
    # def textBBoxSizesPerClass(self, dataframe, writepath = './plot_sizes'):
        
    #     '''plot class by size and write associated data to text'''
        
    #     time = str(datetime.datetime.now()).split('.', 1)[0]
    #     ##get dataframe summary and exclude count
    #     classes = list(set(dataframe.clss))
    #     for clss in classes:
    #         df = dataframe[dataframe.clss == clss].describe().round()
        