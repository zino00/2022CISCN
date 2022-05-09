@main def exec(cpgFile: String, projectFolder: String, outFile: String) = {
   loadCpg(cpgFile)
   (cpg.local ++ 
   cpg.method.callIn
   ).toJsonPretty |> outFile
   delete(projectFolder)
}
