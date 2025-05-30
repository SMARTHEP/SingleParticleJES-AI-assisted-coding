"""
Core functionality for SmartHEP SingleParticleJES package.

This module contains the optimized implementation of the SingleParticleJES
analysis algorithm using ROOT's RDataFrame for efficient data processing.
"""

import ROOT
import sys
import os
import logging
from typing import Optional, Union, List

# Configure logging
logger = logging.getLogger(__name__)

class SingleParticleJESAnalyzer:
    """
    Analyzer class for Single Particle Jet Energy Scale calibration studies.
    
    This class implements an optimized version of the SingleParticleJES analysis
    algorithm using ROOT's RDataFrame for efficient data processing.
    """
    
    def __init__(self, 
                 input_files: Union[str, List[str]], 
                 output_filename: str = "analysis_output.root",
                 tree_name: str = "CollectionTree"):
        """
        Initialize the SingleParticleJES analyzer.
        
        Args:
            input_files: Path to input xAOD ROOT file(s). Can be a single string or list of strings.
            output_filename: Path to output ROOT file for histograms.
            tree_name: Name of the TTree in the input file.
        """
        self.input_files = input_files
        self.output_filename = output_filename
        self.tree_name = tree_name
        self.cluster_collection = "CaloCalTopoClusters"
        self.particle_collection = "TruthParticles"
        self.df = None
        self.output_file = None
        
        # Initialize ROOT
        try:
            ROOT.xAOD.Init()
            ROOT.xAOD.CaloClusterAuxContainer_v2()
            ROOT.xAOD.TruthParticleAuxContainer_v1()
        except Exception as e:
            logger.error(f"Failed to initialize ROOT xAOD: {e}")
            raise RuntimeError(f"Failed to initialize ROOT xAOD: {e}")
            
        # Enable multi-threading
        ROOT.EnableImplicitMT()
        logger.info(f"Implicit Multi-Threading enabled using {ROOT.GetThreadPoolSize()} threads.")
    
    def setup_output_file(self) -> None:
        """
        Set up the output ROOT file for histograms.
        
        Raises:
            RuntimeError: If the output file cannot be created.
        """
        self.output_file = ROOT.TFile.Open(self.output_filename, "RECREATE")
        if not self.output_file or self.output_file.IsZombie():
            logger.error(f"Could not open output file {self.output_filename}")
            raise RuntimeError(f"Could not open output file {self.output_filename}")
        
        self.output_file.cd()
        logger.info(f"Created output file: {self.output_filename}")
    
    def create_dataframe(self) -> None:
        """
        Create the RDataFrame from the input file(s).
        
        Raises:
            RuntimeError: If the RDataFrame cannot be created.
        """
        from xAODDataSource import Helpers
        
        logger.info(f"Processing file(s): {self.input_files}")
        try:
            self.df = Helpers.MakexAODDataFrame(self.input_files)
        except Exception as e:
            logger.error(f"Failed to create RDataFrame: {e}")
            raise RuntimeError(f"Failed to create RDataFrame: {e}")
        
        # Get the initial number of events
        n_total_events = self.df.Count().GetValue()
        if n_total_events == 0:
            logger.error(f"Input file(s) contain no events in the TTree '{self.tree_name}'")
            raise RuntimeError(f"Input file(s) contain no events in the TTree '{self.tree_name}'")
        
        logger.info(f"Total events in TTree: {n_total_events}")
    
    def define_variables(self):
        """
        Define variables and apply filters to the RDataFrame.
        
        Returns:
            ROOT.RDF.RNode: The filtered and defined RDataFrame.
        """
        # Define cluster and particle counts
        df_clusters_and_particles = self.df.Define("nClusters", f"{self.cluster_collection}.size()")
        df_clusters_and_particles = df_clusters_and_particles.Define("nParticles", f"{self.particle_collection}.size()")
        
        # Filter events: require at least 1 particle and 1 cluster
        df_filtered = df_clusters_and_particles.Filter("nClusters >= 1", "At least 1 cluster")
        df_filtered = df_filtered.Filter("nParticles >= 1", "At least 1 particle")
        
        # Filter for pions (PDGID=211)
        df_filtered = df_filtered.Define("pdgId_lead", f"{self.particle_collection}.at(0)->pdgId()")
        df_filtered_PDGID = df_filtered.Filter("pdgId_lead==211", "At least 1 pion")
        
        # Define the energy of the leading cluster (MeV to GeV)
        df_defined = df_filtered_PDGID.Define("leading_cluster_e", 
                                             f"{self.cluster_collection}.at(0)->rawE() / 1000.0")
        
        # Define response calculation
        response_code = self._get_response_code()
        df_defined = df_defined.Define("response", response_code)
        
        # Define additional variables
        df_defined = df_defined.Define("lead_particle_pt", f"{self.particle_collection}.at(0)->pt()/1000.")
        df_defined = df_defined.Define("lead_particle_eta", f"{self.particle_collection}.at(0)->eta()")
        
        return df_defined, df_clusters_and_particles, df_filtered_PDGID
    
    def _get_response_code(self) -> str:
        """
        Get the C++ code for calculating the response.
        
        Returns:
            str: C++ code for response calculation.
        """
        return f"""
            // Check if there are indeed at least 2 clusters (filter should ensure this, but defensive coding)
            if ({self.cluster_collection}.size() < 2) {{
                return -1.0f; // Return a dummy value
            }}
            
            auto& clusters = {self.cluster_collection}; // Reference for convenience
            auto& particles = {self.particle_collection}; // 
            
            // Create Lorentz vectors for the leading cluster and particle (assuming pt-sorted)
            // Since LorentzVector wants pT and not energy, we'll give it pT

            float cluster_pt = sqrt(clusters.at(0)->rawE()*clusters.at(0)->rawE() - clusters.at(0)->rawM()*clusters.at(0)->rawM())/TMath::CosH(clusters.at(0)->rawEta());

            ROOT::Math::PtEtaPhiMVector cluster_lv(cluster_pt, clusters.at(0)->rawEta(), clusters.at(0)->rawPhi(), clusters.at(0)->rawM());
            ROOT::Math::PtEtaPhiMVector particle_lv(particles.at(0)->pt(), particles.at(0)->eta(), clusters.at(0)->phi(), clusters.at(0)->m());

            
            // pT response 
            float response = cluster_lv.Pt()/particle_lv.Pt();
            return response;
        """
    
    def book_histograms(self, df_defined, df_clusters_and_particles, df_filtered_PDGID):
        """
        Book histograms using the defined columns.
        
        Args:
            df_defined: The fully defined RDataFrame.
            df_clusters_and_particles: RDataFrame with cluster and particle counts.
            df_filtered_PDGID: RDataFrame filtered by PDGID.
            
        Returns:
            dict: Dictionary of booked histograms.
        """
        # Histogram models
        h_nClusters_model = ROOT.RDF.TH1DModel("h_nClusters", "Number of Clusters;N_{Clusters};Events", 20, -0.5, 19.5)
        h_nParticles_model = ROOT.RDF.TH1DModel("h_nParticles", "Number of Particles;N_{Particles};Events", 20, -0.5, 19.5)
        h_leading_cluster_e_model = ROOT.RDF.TH1DModel("h_leading_cluster_e", "Leading Cluster E;E^{lead cluster} [GeV];Events", 100, 0, 500)
        h_PDGIDs_model = ROOT.RDF.TH1DModel("h_PDGIDs", "Leading Cluster PDGID;PDGID^{lead cluster};Events", 1000, 0, 1000)
        h_inclusive_response_model = ROOT.RDF.TH1DModel("h_inclusive_response", "Response (inclusive); p_{T,cluster}/p_{T,particle};Events", 100, 0, 3)
        h_3d_response_model = ROOT.RDF.TH3DModel("h_response", "Response (binned); p_{T,cluster}/p_{T,particle},p_{T,particle},eta;Events", 50, 0, 2, 100, 0, 500, 60, -3, 3)
        
        # Book histograms
        histograms = {}
        histograms["h_nClusters"] = df_clusters_and_particles.Histo1D(h_nClusters_model, "nClusters")
        histograms["h_nParticles"] = df_clusters_and_particles.Histo1D(h_nParticles_model, "nParticles")
        histograms["h_PDGIDs"] = df_filtered_PDGID.Histo1D(h_PDGIDs_model, "pdgId_lead")
        histograms["h_leading_cluster_e"] = df_defined.Histo1D(h_leading_cluster_e_model, "leading_cluster_e")
        histograms["h_inclusive_response"] = df_defined.Histo1D(h_inclusive_response_model, "response")
        histograms["h_3d_response"] = df_defined.Histo3D(h_3d_response_model, "response", "lead_particle_pt", "lead_particle_eta")
        
        # Set directory for histograms
        for name, hist in histograms.items():
            hist.SetDirectory(self.output_file)
        
        return histograms, df_defined
    
    def save_histograms(self, histograms):
        """
        Save histograms to the output file.
        
        Args:
            histograms: Dictionary of histograms to save.
        """
        logger.info(f"Saving histograms to: {self.output_filename}")
        self.output_file.cd()
        
        # Get histogram values and write to file
        for name, hist in histograms.items():
            hist_ptr = hist.GetValue()
            hist_ptr.Write()
        
        self.output_file.Close()
        logger.info("Histograms saved.")
    
    def run_analysis(self):
        """
        Run the full analysis pipeline.
        """
        try:
            # Setup
            self.setup_output_file()
            self.create_dataframe()
            
            # Define variables and book histograms
            df_defined, df_clusters_and_particles, df_filtered_PDGID = self.define_variables()
            histograms, df_defined = self.book_histograms(df_defined, df_clusters_and_particles, df_filtered_PDGID)
            
            # Generate report
            logger.info("Event loop running...")
            report = df_defined.Report()
            
            # Save histograms
            self.save_histograms(histograms)
            
            # Print report
            logger.info("\n--- Analysis Report ---")
            report.Print()
            logger.info("---------------------\n")
            
            logger.info("Analysis finished successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False


def run_single_particle_jes_analysis(input_files, output_filename="analysis_output.root", tree_name="CollectionTree"):
    """
    Run the SingleParticleJES analysis on the given input files.
    
    Args:
        input_files: Path to input xAOD ROOT file(s). Can be a single string or list of strings.
        output_filename: Path to output ROOT file for histograms.
        tree_name: Name of the TTree in the input file.
        
    Returns:
        bool: True if analysis completed successfully, False otherwise.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    analyzer = SingleParticleJESAnalyzer(input_files, output_filename, tree_name)
    return analyzer.run_analysis()
