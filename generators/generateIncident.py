#!/usr/bin/env python

import stix

from stix.core import STIXPackage, STIXHeader
from datetime import datetime
from cybox.common import Time

from stix.incident import Incident,ImpactAssessment, AffectedAsset
from stix.incident import Time as incidentTime # different type than common:Time

from stix.common import InformationSource
from stix.common import Confidence
from stix.common import Identity

from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.simple_marking import SimpleMarkingStructure

def build_stix( input_dict ):
    # setup stix document
    stix_package = STIXPackage()
    stix_header = STIXHeader()

    stix_header.description = "Incident report for " + input_dict['organization']
    stix_header.add_package_intent ("Incident")

    # Add handling requirements if needed
    if input_dict['sensitive'] == "True":
        mark = SimpleMarkingStructure()
        mark.statement = "Sensitive"
        mark_spec = MarkingSpecification()
        mark_spec.marking_structures.append(mark)
        stix_header.handling = Marking(mark_spec)


    stix_package.stix_header = stix_header

    # add incident and confidence
    incident = Incident()
    incident.description = input_dict['description']
    incident.confidence = input_dict['confidence']

    # add incident reporter
    incident.reporter = InformationSource()
    incident.reporter.description = "Person who reported the incident"

    incident.reporter.time = Time()
    incident.reporter.time.produced_time = datetime.strptime(input_dict['timestamp'], "%Y-%m-%d") # when they submitted it

    incident.reporter.identity = Identity()
    incident.reporter.identity.name = input_dict['submitter']

    # incident time is a complex object with support for a bunch of different "when stuff happened" items
    incident.time = incidentTime()
    incident.title = "Breach of " + input_dict['organization']
    incident.time.incident_discovery = datetime.strptime(input_dict['timestamp'], "%Y-%m-%d") # when they submitted it

    # add the impact
    impact = ImpactAssessment()
    impact.add_effect(input_dict['damage'])
    incident.impact_assessment = impact

    #Add the thing that was stolen
    jewels = AffectedAsset()
    jewels.type_ = input_dict['asset']
    incident.add_affected_asset (jewels)

    # add the victim
    incident.add_victim (input_dict['organization'])

    stix_package.add_incident(incident)

    return stix_package

if __name__ == '__main__':
    # emit STIX
    pkg = build_stix()
    print pkg.to_xml()
