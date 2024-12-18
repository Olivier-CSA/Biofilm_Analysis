// @File(label = "Dossier input", style = "directory") input
// @File(label = "Dossier output", style = "directory") output
// @String(label = "Suffixe des fichiers à analyser", value = ".czi") suffixe

lireDossier(input);

function lireDossier(input){
	liste = getFileList(input);
	for(i=0; i<liste.length;i++) {
		if(File.isDirectory(input + liste[i]))
			lireDossier("" + input + liste[i]);
		if(endsWith(liste[i], suffixe))
			analyseFichier(input, output, liste[i]);
	}
	//saveAs("Results", output + "/Resultats.csv");
}

function analyseFichier(input, output, fichier){
	setBatchMode(true);
	run("Bio-Formats", "open=[" + input + "/" + fichier + "] autoscale color_mode=Colorized rois_import=[ROI manager] split_channels view=Hyperstack stack_order=XYCZT");
	close();
	selectImage("input/" + fichier + " - C=0");
	//id = getImageID();
	rename("stack");
	run("Gaussian Blur 3D...", "x=1 y=1 z=1");
	
	run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box dots_size=10 font_size=10 store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=none");
	run("3D Objects Counter", "threshold=90 slice=4 min.=2 max.=1742400 surfaces centres_of_masses statistics");
	selectImage("Surface map of stack");
	run("3D Project...", "projection=[Brightest Point] axis=Y-Axis slice=1 initial=0 total=360 rotation=10 lower=1 upper=255 opacity=0 surface=100 interior=50 interpolate");
	save(output + "/Images3D_" + fichier + ".gif");
	selectWindow("Statistics for stack");
	saveAs("Results", output + "/Resultats_" + fichier + ".csv");
	close();
	close();
	close();
	close();
}
