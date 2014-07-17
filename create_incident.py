#!/usr/bin/env python

import stix

from stix.core import STIXPackage, STIXHeader
from datetime import datetime
from cybox.common import Time

from stix.incident import Incident,AffectedAsset
from stix.incident import Time as incidentTime # different type than common:Time

from stix.common import InformationSource
from stix.common import Confidence
from stix.common import Identity

from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.simple_marking import SimpleMarkingStructure

'''
    required fields:
        - when did it happen?
        - What was stolen or disrupted? type of asset as AssetTypeVocab
        - how sure are you? as confidence (low, med, high)
        - do you want to share with other affected organizations? (default to sensitive handling - not shared out)
        - reporter name as Reporter 
        - description as prose
        - organization name as Victim

    un-used fields
        - "nonpublicdata" (if they're reporting it, was clearly important)
        - LossEstimation (not known at the time of report in 99% of cases)
        - AttributedActors (never known)
'''
# setup stix document
stix_package = STIXPackage()
stix_header = STIXHeader()

stix_header.description = "Breach report for $ORG"
stix_header.add_package_intent ("Incident")

# Add handling requirements
mark = SimpleMarkingStructure()
mark.statement = "Sensitive"
mark_spec = MarkingSpecification()
mark_spec.marking_structures.append(mark)
stix_header.handling = Marking(mark_spec)


# stamp with creator
stix_header.information_source = InformationSource()
stix_header.information_source.description = "Person who reported the breach"

stix_header.information_source.time = Time()
stix_header.information_source.time.produced_time = datetime.strptime('2001-01-01', "%Y-%m-%d") # when they submitted it

stix_header.information_source.identity = Identity()
stix_header.information_source.identity.name = "Gavin McDodgeson, P.I."

stix_package.stix_header = stix_header

# add incident and confidence
breach = Incident()
breach.description = "Sultry yet hard-boiled account of what happened"
breach.confidence = Confidence("High") 

# incident time is a complex object with support for a bunch of different "when stuff happened" items
breach.time = incidentTime()
breach.title = "Breach of $ORG"
breach.time.initial_compromise = datetime.strptime('1999-12-31', "%Y-%m-%d") # when they think it happened
breach.time.incident_discovery = datetime.strptime('2001-01-01', "%Y-%m-%d") # when they submitted it

# Add the thing that was stolen
jewels = AffectedAsset()
jewels.type_ = "Source Code" #what they took
jewels.description = "Priceless intellectual property" # how the victim describes it in prose
breach.add_affected_asset (jewels) 
breach.add_victim ("$ORG - LLC in the caymans")


stix_package.add_incident(breach)



# Finalize and emit STIX

print stix_package.to_xml() 
